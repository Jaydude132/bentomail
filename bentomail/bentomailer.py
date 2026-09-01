# Author: Jason Marencic
# June 2, 2026

import os
from typing import Optional, List, Union, overload
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import jinja2

from . import themes
from .components import (
    Header,
    Hero,
    Card,
    LineBreak,
    Report,
    Notice,
    Section,
    Footer,
    FooterLink,
    CriticalNotice,
    ErrorNotice,
    WarningNotice,
    ImportantNotice,
    SuccessNotice,
    InfoNotice,
    LineChart,
    BarChart,
    PieChart,
)

# SMTP Environment bootstrap configuration
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")


def _resolve_color(color_val: str, theme: Optional[themes.EmailTheme] = None) -> str:
    if not color_val:
        return ""
    color_str = str(color_val).strip()
    if theme:
        theme_map = {
            "SUCCESS": theme.success_color,
            "OK": theme.ok_color,
            "INFO": theme.info_color,
            "WARNING": theme.warning_color,
            "MINOR": theme.minor_color,
            "ERROR": theme.error_color,
            "CRITICAL": theme.critical_color,
            "IMPORTANT": theme.important_color,
        }
        val_upper = color_str.upper()
        if val_upper in theme_map:
            return theme_map[val_upper]
    return color_str


class BentoMailer:
    def __init__(
        self,
        recipients: Optional[List[str]] = None,
        subject: Optional[str] = None,
        cc_recipient: Optional[Union[str, List[str]]] = None,
        sender: Optional[str] = None,
        theme: themes.EmailTheme = themes.NEUTRAL,
    ) -> None:
        self.sender: str = sender or os.getenv("SENDER_EMAIL", "sender@example.com")
        self.smtp_server: str = os.getenv("SMTP_SERVER", "localhost")
        try:
            self.smtp_port: int = int(os.getenv("SMTP_PORT", "25"))
        except (ValueError, TypeError):
            self.smtp_port = 25

        # Authentication & Security
        self.smtp_user: Optional[str] = os.getenv("SMTP_USER")
        self.smtp_pass: Optional[str] = os.getenv("SMTP_PASS")

        # Auto-detect security protocols based on standard ports, or allow explicit overrides
        self.use_tls: bool = (
            str(os.getenv("SMTP_USE_TLS", "False")).lower() in ("true", "1", "yes")
            or self.smtp_port == 587
        )
        self.use_ssl: bool = (
            str(os.getenv("SMTP_USE_SSL", "False")).lower() in ("true", "1", "yes")
            or self.smtp_port == 465
        )

        self.theme: themes.EmailTheme = theme
        self.recipients: Optional[List[str]] = (
            [r for r in recipients] if recipients else None
        )
        self.subject: Optional[str] = subject
        self.cc_recipient: Optional[Union[str, List[str]]] = cc_recipient
        self._html_body: Optional[str] = None
        self._plain_text_body: Optional[str] = None
        self._alert_content: Optional[str] = None

        self._attachments: List = []  # Downloadable attachments (PDF, CSV, etc.)
        self._inline_images: List = (
            []
        )  # Embedded inline graphics (charts, graphs, etc.)

        self.header_block: Optional[Header] = None
        self.hero_block: Optional[Hero] = None
        self.footer_block: Optional[Footer] = None
        self._components: List = []

    def add_linebreak(self) -> None:
        """Terminates the current card row early or inserts a vertical spacer."""
        self._components.append(LineBreak())

    def add_placeholder(self, colspan: int = 1) -> None:
        """Appends a transparent spacer block to align or center adjacent cards."""
        self._components.append(Card(invisible=True, colspan=colspan))

    # =========================================================================
    # --- 1. GLOBAL HEADER BUILDER ---
    # =========================================================================
    @overload
    def create_header(self, header: Header) -> None: ...

    @overload
    def create_header(
        self,
        *,
        description: str = "",
        title: str = "",
        subtitle: str = "",
        color: Optional[str] = None,
    ) -> None: ...

    def create_header(self, header: Optional[Header] = None, **kwargs) -> None:
        """Instantiates or overwrites the global Header component."""
        self.header_block = header if header is not None else Header(**kwargs)

    # =========================================================================
    # --- 2. GLOBAL HERO BUILDER ---
    # =========================================================================
    @overload
    def create_hero(self, hero: Hero) -> None: ...

    @overload
    def create_hero(
        self,
        *,
        badge: str = "",
        title: str = "",
        description: str = "",
        from_color: Optional[str] = None,
        to_color: Optional[str] = None,
        accent_color: Optional[str] = None,
    ) -> None: ...

    def create_hero(self, hero: Optional[Hero] = None, **kwargs) -> None:
        """Instantiates or overwrites the global Hero component."""
        self.hero_block = hero if hero is not None else Hero(**kwargs)

    # =========================================================================
    # --- 3. GLOBAL FOOTER BUILDER ---
    # =========================================================================
    @overload
    def create_footer(self, footer: Footer) -> None: ...

    @overload
    def create_footer(
        self,
        *,
        line1: str = "",
        line2: str = "",
        links: Optional[List[Union[dict, FooterLink]]] = None,
    ) -> None: ...

    def create_footer(self, footer: Optional[Footer] = None, **kwargs) -> None:
        """Instantiates or overwrites the global Footer component."""
        if footer is not None:
            self.footer_block = footer
        else:
            links_raw = kwargs.get("links", [])
            links_cleaned = []
            for l in links_raw:
                if isinstance(l, dict):
                    links_cleaned.append(FooterLink(**l))
                else:
                    links_cleaned.append(l)
            self.footer_block = Footer(
                line1=kwargs.get("line1", ""),
                line2=kwargs.get("line2", ""),
                links=links_cleaned,
            )

    # =========================================================================
    # --- 4. CARD GRID BUILDER ---
    # =========================================================================
    @overload
    def add_card(self, card: Card) -> None: ...

    @overload
    def add_card(
        self,
        *,
        title: str = "",
        value: str = "",
        label: str = "",
        color: Optional[str] = None,
        colspan: Optional[int] = None,
    ) -> None: ...

    def add_card(self, card: Optional[Card] = None, **kwargs) -> None:
        """Appends a new metric Card to the pipeline."""
        self._components.append(card if card is not None else Card(**kwargs))

    # =========================================================================
    # --- 5. DATA TABLE (REPORT) BUILDER ---
    # =========================================================================
    @overload
    def add_report(self, report: Report) -> None: ...

    @overload
    def add_report(
        self,
        *,
        title: str = "",
        headers: Optional[List[str]] = None,
        data: Optional[List[List[str]]] = None,
        highlight_row_index: Optional[int] = None,
        header_color: str = "#1E293B",
        tip: str = "",
        colspan: int = 1,
        title_align: str = "left",
    ) -> None: ...

    def add_report(self, report: Optional[Report] = None, **kwargs) -> None:
        """Appends a new Report table to the pipeline."""
        if report is not None:
            self._components.append(report)
        else:
            self._components.append(
                Report(
                    title=kwargs.get("title", ""),
                    headers=(
                        kwargs.get("headers")
                        if kwargs.get("headers") is not None
                        else []
                    ),
                    data=kwargs.get("data") if kwargs.get("data") is not None else [],
                    highlight_row_index=kwargs.get("highlight_row_index"),
                    header_color=kwargs.get("header_color", "#1E293B"),
                    tip=kwargs.get("tip", ""),
                    colspan=kwargs.get("colspan", 1),
                    title_align=kwargs.get("title_align", "left"),
                )
            )

    def add_section(self, section: Section) -> None:
        self._components.append(section)

    def add_notice(self, notice: Notice) -> None:
        self._components.append(notice)

    def add_critical(self, message: str, colspan: int = 2) -> None:
        self.add_notice(CriticalNotice(message=message, colspan=colspan))

    def add_error(self, message: str, colspan: int = 2) -> None:
        self.add_notice(ErrorNotice(message=message, colspan=colspan))

    def add_warning(self, message: str, colspan: int = 2) -> None:
        self.add_notice(WarningNotice(message=message, colspan=colspan))

    def add_important(self, message: str, colspan: int = 2) -> None:
        self.add_notice(ImportantNotice(message=message, colspan=colspan))

    def add_info(self, message: str, colspan: int = 2) -> None:
        self.add_notice(InfoNotice(message=message, colspan=colspan))

    def add_success(self, message: str, colspan: int = 2) -> None:
        self.add_notice(SuccessNotice(message=message, colspan=colspan))

    # --- High-Level Pure Data Chart Pipeline Builders ---
    def add_line_chart(self, x: list, y: list, **kwargs) -> None:
        self._components.append(LineChart(x=x, y=y, **kwargs))

    def add_bar_chart(self, categories: list, values: list, **kwargs) -> None:
        self._components.append(
            BarChart(categories=categories, values=values, **kwargs)
        )

    def add_pie_chart(self, labels: list, sizes: list, **kwargs) -> None:
        self._components.append(PieChart(labels=labels, sizes=sizes, **kwargs))

    def add_attachment(
        self, file_path: str, custom_filename: Optional[str] = None
    ) -> None:
        """
        Loads a local file, wraps it as a standard downloadable MIME attachment,
        and queues it inside the outer 'mixed' pipeline envelope.
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Attachment file not found: {file_path}")

        filename = custom_filename or os.path.basename(file_path)
        with open(file_path, "rb") as f:
            attachment_data = f.read()

        # Wrap as generic binary application attachment
        mime_part = MIMEApplication(attachment_data)
        mime_part.add_header("Content-Disposition", "attachment", filename=filename)

        # This appends it cleanly to our isolated downloadable files pool!
        self._attachments.append(mime_part)

    def _validate_routing_fields(self) -> None:
        if not self.recipients:
            raise ValueError("recipients is not defined")
        if not self.subject:
            raise ValueError("subject is not defined")

    def _compute_card_widths(self, cards: list) -> None:
        """
        Computes exact relative width percentages for a row of cards,
        supporting both equal-width auto-spanning and explicit colspans.
        """
        all_unassigned = all(c.colspan is None for c in cards)
        num_cards = len(cards)

        if all_unassigned:
            # 1. Equal-width distribution (100% - standard 2% gutters)
            total_spacers_pct = (num_cards - 1) * 2
            available_pct = 100 - total_spacers_pct
            equal_width = available_pct / num_cards
            for c in cards:
                c.width_pct = f"{equal_width}%"
                c.colspan = 1  # Fallback for old templates
        else:
            # 2. Mixed: some have explicit colspans, some do not.
            explicit_sum = sum(c.colspan for c in cards if c.colspan is not None)
            unassigned_count = sum(1 for c in cards if c.colspan is None)

            remaining_colspan = 4 - explicit_sum
            if unassigned_count > 0:
                base_val = max(1, remaining_colspan // unassigned_count)
                remainder = remaining_colspan % unassigned_count
                for c in cards:
                    if c.colspan is None:
                        c.colspan = base_val + (1 if remainder > 0 else 0)
                        if remainder > 0:
                            remainder -= 1

            # 3. Dynamic Auto-Padding: If the row is under-filled, automatically append a transparent spacer
            total_resolved_colspan = sum(c.colspan for c in cards)
            if total_resolved_colspan < 4:
                missing_colspan = 4 - total_resolved_colspan
                placeholder = Card(colspan=missing_colspan, invisible=True)
                cards.append(placeholder)

            # Translate resolved 1-4 colspans to standard percentage targets
            for c in cards:
                if c.colspan == 4:
                    c.width_pct = "100%"
                elif c.colspan == 3:
                    c.width_pct = "74.5%"
                elif c.colspan == 2:
                    c.width_pct = "49%"
                else:
                    c.width_pct = "23.5%"

    # --- Sequential Layout Clustering Engine ---
    def _group_component_list(self, components: List) -> List[dict]:
        rows = []
        card_block = []
        content_row_buffer = []
        current_row_colspan = 0

        def flush_cards():
            nonlocal card_block
            if card_block:
                card_rows = []
                row_cards = []
                current_row_colspan = 0
                for c in card_block:
                    if isinstance(c, LineBreak):
                        # Split card row early on LineBreak
                        if row_cards:
                            card_rows.append({"type": "cards", "items": row_cards})
                            row_cards = []
                            current_row_colspan = 0
                        continue

                    c_colspan = c.colspan if c.colspan is not None else 1
                    if current_row_colspan + c_colspan > 4:
                        card_rows.append({"type": "cards", "items": row_cards})
                        row_cards = []
                        current_row_colspan = 0
                    row_cards.append(c)
                    current_row_colspan += c_colspan
                if row_cards:
                    card_rows.append({"type": "cards", "items": row_cards})

                # Compute custom proportional card widths dynamically for each row
                for r in card_rows:
                    self._compute_card_widths(r["items"])
                    rows.append(r)
                card_block = []

        def flush_contents():
            nonlocal content_row_buffer, current_row_colspan
            if content_row_buffer:
                rows.append({"type": "components", "items": content_row_buffer})
                content_row_buffer = []
                current_row_colspan = 0

        for comp in components:
            if isinstance(comp, Card):
                flush_contents()
                card_block.append(comp)
            elif isinstance(comp, LineBreak):
                if card_block:
                    card_block.append(comp)
                else:
                    flush_cards()
                    content_row_buffer.append(comp)
                    current_row_colspan += comp.colspan
            else:
                flush_cards()
                if current_row_colspan + comp.colspan > 2:
                    flush_contents()
                content_row_buffer.append(comp)
                current_row_colspan += comp.colspan

        flush_cards()
        flush_contents()
        return rows

    def _group_components_for_layout(
        self, components_list: Optional[List] = None
    ) -> List[dict]:
        rows = []
        card_block = []
        content_row_buffer = []
        current_row_colspan = 0

        target_components = (
            components_list if components_list is not None else self._components
        )

        def flush_cards():
            nonlocal card_block
            if card_block:
                card_rows = []
                row_cards = []
                current_row_colspan = 0
                for c in card_block:
                    if isinstance(c, LineBreak):
                        # Split card row early on LineBreak
                        if row_cards:
                            card_rows.append({"type": "cards", "items": row_cards})
                            row_cards = []
                            current_row_colspan = 0
                        continue

                    c_colspan = c.colspan if c.colspan is not None else 1
                    if current_row_colspan + c_colspan > 4:
                        card_rows.append({"type": "cards", "items": row_cards})
                        row_cards = []
                        current_row_colspan = 0
                    row_cards.append(c)
                    current_row_colspan += c_colspan
                if row_cards:
                    card_rows.append({"type": "cards", "items": row_cards})

                # Compute custom proportional card widths dynamically for each row
                for r in card_rows:
                    self._compute_card_widths(r["items"])
                    rows.append(r)
                card_block = []

        def flush_contents():
            nonlocal content_row_buffer, current_row_colspan
            if content_row_buffer:
                rows.append({"type": "components", "items": content_row_buffer})
                content_row_buffer = []
                current_row_colspan = 0

        for comp in target_components:
            if isinstance(comp, Card):
                flush_contents()
                card_block.append(comp)
            elif isinstance(comp, LineBreak):
                if card_block:
                    card_block.append(comp)
                else:
                    flush_cards()
                    content_row_buffer.append(comp)
                    current_row_colspan += comp.colspan
            elif isinstance(comp, Section):
                flush_contents()
                flush_cards()
                grouped_widgets = self._group_component_list(comp.widgets)
                rows.append(
                    {
                        "type": "section",
                        "title": comp.title,
                        "subtitle": comp.subtitle,
                        "title_align": comp.title_align,
                        "widgets": grouped_widgets,
                    }
                )
            else:
                flush_cards()
                if current_row_colspan + comp.colspan > 2:
                    flush_contents()
                content_row_buffer.append(comp)
                current_row_colspan += comp.colspan

        flush_cards()
        flush_contents()
        return rows

    # --- Idempotent Dynamic Chart Preprocessor ---
    def _render_and_register_charts(self) -> List:
        """
        Scans components for raw chart data, renders them to inline images,
        and returns a processed copy of the components with compiled Chart references.
        """
        import uuid
        from email.mime.image import MIMEImage
        from .components import BaseChart, Chart, Section

        # 1. Smarter check: Only catch missing matplotlib package installation
        try:
            import matplotlib
        except ImportError as e:
            raise ImportError(
                "Matplotlib is required for inline chart rendering. "
                "Please run: pip install matplotlib"
            ) from e

        # 2. This import is now OUTSIDE the try/except block.
        # If there is a typo or saving issue, Python will tell you the exact line!
        from .chart_renderer import render_chart_to_png

        def process_component_tree(comp_list):
            new_list = []
            for comp in comp_list:
                if isinstance(comp, BaseChart):
                    # Render data to binary PNG bytes
                    png_bytes = render_chart_to_png(comp, self.theme)

                    # Build inline CID asset
                    cid = f"chart_{uuid.uuid4().hex[:8]}"
                    mime_img = MIMEImage(png_bytes)
                    mime_img.add_header("Content-ID", f"<{cid}>")
                    mime_img.add_header(
                        "Content-Disposition", "inline", filename=f"{cid}.png"
                    )

                    # Save inline image
                    self._inline_images.append(mime_img)

                    # Swap for layout visual target
                    new_list.append(
                        Chart(cid=cid, title=comp.title, colspan=comp.colspan)
                    )
                elif isinstance(comp, Section):
                    copied_widgets = process_component_tree(comp.widgets)
                    new_section = Section(
                        title=comp.title,
                        subtitle=comp.subtitle,
                        title_align=comp.title_align,
                        widgets=copied_widgets,
                    )
                    new_list.append(new_section)
                else:
                    new_list.append(comp)
            return new_list

        return process_component_tree(self._components)

    # --- HTML Rendering Engine (Jinja2) ---
    def compile_dashboard_html(self) -> str:
        # Clear previous compiled charts to prevent duplicate attachments on multiple compilations
        self._inline_images = [
            img
            for img in self._inline_images
            if not img.get("Content-ID", "").startswith("<chart_")
        ]

        # Preprocess charts and get layout-ready component copy
        processed_components = self._render_and_register_charts()

        # Native Jinja2 package routing (Safe for PyPI wheels)
        loader = jinja2.PackageLoader("bentomail", "templates")
        env = jinja2.Environment(loader=loader, autoescape=True)
        template: jinja2.Template = env.get_template("dashboard.jinja")

        grouped_components = self._group_components_for_layout(processed_components)

        return template.render(
            theme=self.theme,
            header=self.header_block,
            hero=self.hero_block,
            footer=self.footer_block,
            components=grouped_components,
            subject=self.subject or "Dashboard Report",
        )

    def as_mime_message(self) -> MIMEMultipart:
        """Assembles and returns the fully packed MIME message (HTML + CID images) without sending it."""
        self._validate_routing_fields()
        dashboard_html = self.compile_dashboard_html()

        # 1. Core Unit
        body_container = MIMEMultipart("related")
        body_container.attach(MIMEText(dashboard_html, "html"))
        for inline_img in self._inline_images:
            body_container.attach(inline_img)

        # 2. Outer Wrapper
        if self._attachments:
            msg = MIMEMultipart("mixed")
            msg.attach(body_container)
            for attachment in self._attachments:
                msg.attach(attachment)
        else:
            msg = body_container

        # 3. Standard SMTP Header Assembly
        msg["Subject"] = self.subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipient.strip() for recipient in self.recipients)

        cc_list: list[str] = []
        if self.cc_recipient is not None:
            if isinstance(self.cc_recipient, str):
                cc_list = [
                    email.strip()
                    for email in self.cc_recipient.split(",")
                    if email.strip()
                ]
            if isinstance(self.cc_recipient, list):
                cc_list = [email.strip() for email in self.cc_recipient]

            msg["Cc"] = ", ".join(cc_list)
            for cc in cc_list:
                if cc not in self.recipients:
                    self.recipients.append(cc)

        return msg

    def send_dashboard(self) -> None:
        """Compiles the dashboard and dispatches it over the configured SMTP relay."""
        msg = self.as_mime_message()

        # Dispatch Relay (with Auth & Encryption Support)
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()

            # Authenticate if credentials exist
            if self.smtp_user and self.smtp_pass:
                server.login(self.smtp_user, self.smtp_pass)

            server.sendmail(self.sender, self.recipients, msg.as_string())

        except Exception as e:
            raise RuntimeError(
                f"Failed to send email via {self.smtp_server}:{self.smtp_port}. Error: {str(e)}"
            )
        finally:
            # Ensure the connection is always closed cleanly
            try:
                server.quit()
            except Exception:
                pass
