# Author: Jason Marencic
# June 2, 2026

import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Union, overload

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
from .layout import group_components


def _chart_alt_text(chart) -> str:
    """
    Describes a chart for screen readers and for clients that block images.

    Uses the caller's own alt_text when they supplied one, otherwise builds a
    description from the chart type and its title.
    """
    if chart.alt_text:
        return chart.alt_text

    kind = {
        LineChart: "Line chart",
        BarChart: "Bar chart",
        PieChart: "Pie chart",
    }.get(type(chart), "Chart")

    return f"{kind}: {chart.title}" if chart.title else kind


class Dashboard:
    """
    Assembles a themed HTML dashboard from a pipeline of components.

    A Dashboard owns layout and rendering only. It has no notion of
    recipients or transport, so it can be handed to any delivery mechanism:
    call to_html() for the raw markup, or to_mime() for a MIME body with the
    inline chart images already attached. BentoMailer extends this class with
    SMTP routing.
    """

    def __init__(
        self,
        theme: themes.EmailTheme = themes.NEUTRAL,
        subject: Optional[str] = None,
        branding: bool = True,
    ) -> None:
        self.theme: themes.EmailTheme = theme
        self.subject: Optional[str] = subject
        self.branding: bool = branding

        self._attachments: List = []  # Downloadable attachments (PDF, CSV, etc.)
        self._inline_images: List = []  # Embedded inline graphics (charts, graphs)

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

    def _has_charts(self, components: List) -> bool:
        """Reports whether a component tree contains any raw chart data."""
        from .components import BaseChart, Section

        for comp in components:
            if isinstance(comp, BaseChart):
                return True
            if isinstance(comp, Section) and self._has_charts(comp.widgets):
                return True
        return False

    # --- Idempotent Dynamic Chart Preprocessor ---
    def _render_and_register_charts(self) -> List:
        """
        Scans components for raw chart data, renders them to inline images,
        and returns a processed copy of the components with compiled Chart references.
        """
        import uuid
        from email.mime.image import MIMEImage
        from .components import BaseChart, Chart, Section

        # Charting is an optional extra, so a dashboard built without any chart
        # components must never reach for matplotlib.
        if not self._has_charts(self._components):
            return list(self._components)

        try:
            import matplotlib  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "Matplotlib is required for inline chart rendering. "
                "Install it with: pip install bentomail[charts]"
            ) from e

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
                        Chart(
                            cid=cid,
                            title=comp.title,
                            colspan=comp.colspan,
                            alt_text=_chart_alt_text(comp),
                        )
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

    # =========================================================================
    # --- HTML RENDERING ENGINE (Jinja2) ---
    # =========================================================================
    def to_html(self) -> str:
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

        grouped_components = group_components(processed_components)

        return template.render(
            theme=self.theme,
            header=self.header_block,
            hero=self.hero_block,
            footer=self.footer_block,
            components=grouped_components,
            branding=self.branding,
            subject=self.subject or "Dashboard Report",
        )

    # Retained so existing pipelines keep working after the rename to to_html.
    compile_dashboard_html = to_html

    def to_mime(self) -> MIMEMultipart:
        """
        Packs the dashboard into a MIME body: the HTML part, any inline chart
        images, and any queued file attachments.

        No routing headers are set. BentoMailer.as_mime_message() adds those.
        """
        dashboard_html = self.to_html()

        # 1. Core Unit
        body_container = MIMEMultipart("related")
        body_container.attach(MIMEText(dashboard_html, "html"))
        for inline_img in self._inline_images:
            body_container.attach(inline_img)

        # 2. Outer Wrapper
        if not self._attachments:
            return body_container

        msg = MIMEMultipart("mixed")
        msg.attach(body_container)
        for attachment in self._attachments:
            msg.attach(attachment)
        return msg
