# Author: Jason Marencic
# June 2, 2026

import textwrap
from typing import List

from .components import (
    BaseChart,
    Card,
    LineBreak,
    Notice,
    Report,
    Section,
    chart_alt_text,
)

# Plain-text mail is conventionally wrapped well short of the terminal width.
WIDTH = 72
COLUMN_GAP = 2

BRANDING_LINE = "Built with BentoMail - https://github.com/jaydude132/bentomail"


def _wrap(text: str, indent: str = "") -> List[str]:
    """Wraps a paragraph to the page width, preserving the given indent."""
    if not text:
        return []
    return textwrap.wrap(
        " ".join(str(text).split()),
        width=WIDTH - len(indent),
        initial_indent=indent,
        subsequent_indent=indent,
    )


def _rule(char: str, indent: str = "") -> str:
    return indent + char * (WIDTH - len(indent))


def _columns(rows: List[List[str]], indent: str, gap: int = COLUMN_GAP) -> List[str]:
    """
    Lays out a table of cells in aligned columns.

    The final column is left unpadded so trailing whitespace never survives
    into the message body.
    """
    if not rows:
        return []

    count = max(len(r) for r in rows)
    padded = [list(r) + [""] * (count - len(r)) for r in rows]
    widths = [max(len(r[i]) for r in padded) for i in range(count)]

    lines = []
    for row in padded:
        cells = [
            cell.ljust(widths[i]) if i < count - 1 else cell
            for i, cell in enumerate(row)
        ]
        lines.append((indent + (" " * gap).join(cells)).rstrip())
    return lines


def _render_cards(cards: List[Card], indent: str) -> List[str]:
    """Renders a run of metric cards as an aligned label/value/note table."""
    rows = [
        [c.title or "", c.value or "", c.label or ""] for c in cards if not c.invisible
    ]
    return _columns(rows, indent)


def _render_report(report: Report, indent: str) -> List[str]:
    lines = []
    if report.title:
        lines.append(indent + report.title.upper())
        lines.append("")

    if not report.data:
        lines.append(indent + "  No data to display.")
        return lines

    body_indent = indent + "  "
    rows = [list(report.headers)] if report.headers else []
    rows += [[str(cell) for cell in row] for row in report.data]
    rendered = _columns(rows, body_indent)

    if report.headers:
        # Underline spans the widest rendered row, not just the header, since
        # the final column is never padded.
        span = max(len(line) for line in rendered) - len(body_indent)
        lines.append(rendered[0])
        lines.append(body_indent + "-" * span)
        rendered = rendered[1:]

    lines.extend(rendered)

    if report.tip:
        lines.append("")
        lines.extend(_wrap(report.tip, body_indent))
    return lines


def _render_notice(notice: Notice, indent: str) -> List[str]:
    label = f"[{notice.header_text.upper()}]"
    body = _wrap(notice.message, indent + " " * (len(label) + 1))
    if not body:
        return [indent + label]

    # Fold the label onto the first wrapped line.
    first = body[0]
    body[0] = indent + label + first[len(indent) + len(label) :]
    return body


def _render_section(section: Section, indent: str) -> List[str]:
    heading = section.title.upper() if section.title else ""
    if section.subtitle:
        heading = f"{heading} | {section.subtitle}" if heading else section.subtitle

    lines = [_rule("-", indent)]
    if heading:
        lines.append(indent + heading)
        lines.append("")
    lines.extend(_render_components(section.widgets, indent + "  "))
    return lines


def _render_components(components: List, indent: str) -> List[str]:
    """Walks a component list, batching consecutive cards so they align."""
    lines: List[str] = []
    card_run: List[Card] = []

    def flush_cards():
        if card_run:
            lines.extend(_render_cards(card_run, indent))
            lines.append("")
            card_run.clear()

    for comp in components:
        if isinstance(comp, Card):
            card_run.append(comp)
            continue

        flush_cards()

        if isinstance(comp, LineBreak):
            continue
        if isinstance(comp, Section):
            lines.extend(_render_section(comp, indent))
        elif isinstance(comp, Report):
            lines.extend(_render_report(comp, indent))
        elif isinstance(comp, Notice):
            lines.extend(_render_notice(comp, indent))
        elif isinstance(comp, BaseChart):
            # The image cannot render here, so its description stands in.
            lines.extend(_wrap(f"[{chart_alt_text(comp)}]", indent))
        lines.append("")

    flush_cards()
    return lines


def render_dashboard_text(dashboard) -> str:
    """
    Renders a Dashboard as the plain-text half of a multipart/alternative
    message, for clients that will not display HTML.
    """
    lines: List[str] = []

    header = dashboard.header_block
    if header:
        if header.description:
            lines.extend(_wrap(header.description.upper()))
        if header.title:
            lines.extend(_wrap(header.title))
        if header.subtitle:
            lines.extend(_wrap(header.subtitle))
        lines.append("")

    hero = dashboard.hero_block
    if hero:
        lines.append(_rule("="))
        if hero.badge:
            lines.extend(_wrap(hero.badge.upper()))
        if hero.title:
            lines.extend(_wrap(hero.title))
        if hero.description:
            lines.append("")
            lines.extend(_wrap(hero.description))
        lines.append(_rule("="))
        lines.append("")

    lines.extend(_render_components(dashboard._components, ""))

    footer = dashboard.footer_block
    if footer:
        lines.append(_rule("-"))
        for line in (footer.line1, footer.line2):
            lines.extend(_wrap(line))
        for link in footer.links:
            lines.append(f"{link.text}: {link.url}")

    if dashboard.branding:
        lines.append("")
        lines.append(BRANDING_LINE)

    # Collapse the runs of blank lines the section builders leave behind.
    output: List[str] = []
    for line in lines:
        if line or (output and output[-1]):
            output.append(line)
    return "\n".join(output).strip() + "\n"
