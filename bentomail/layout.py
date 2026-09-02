# Author: Jason Marencic
# June 2, 2026

from dataclasses import replace
from typing import List

from .components import Card, LineBreak, Section

# The card grid is four columns wide, separated by a fixed percentage gutter.
# Every width in the rendered dashboard derives from these two numbers.
GRID_COLUMNS = 4
GUTTER_PCT = 2.0

# Content components (reports, notices, charts) sit on a coarser two-column
# track rather than the four-column card grid.
CONTENT_COLUMNS = 2


def _percent(value: float) -> str:
    """Formats a width percentage without a redundant trailing zero."""
    return f"{value:.4f}".rstrip("0").rstrip(".") + "%"


def column_width(colspan: int) -> str:
    """Width of a cell spanning the given number of grid columns."""
    return _percent(colspan * (100.0 + GUTTER_PCT) / GRID_COLUMNS - GUTTER_PCT)


def equal_width(count: int) -> str:
    """Width of one cell when a row is split evenly between its cards."""
    return _percent((100.0 - (count - 1) * GUTTER_PCT) / count)


def resolve_card_widths(cards: List[Card]) -> List[Card]:
    """
    Resolves the relative widths for one row of cards, supporting both
    equal-width auto-spanning and explicit colspans.

    Works on copies rather than the caller's components, so recompiling a
    dashboard always starts from the colspans that were originally set.
    """
    resolved = [replace(c) for c in cards]

    if all(c.colspan is None for c in resolved):
        # 1. Even distribution across however many cards the row holds.
        width = equal_width(len(resolved))
        for card in resolved:
            card.width_pct = width
            card.colspan = 1
        return resolved

    # 2. Mixed row: share the remaining columns between the unassigned cards.
    explicit_sum = sum(c.colspan for c in resolved if c.colspan is not None)
    unassigned = [c for c in resolved if c.colspan is None]

    if unassigned:
        remaining = GRID_COLUMNS - explicit_sum
        base = max(1, remaining // len(unassigned))
        leftover = remaining % len(unassigned)
        for card in unassigned:
            card.colspan = base + (1 if leftover > 0 else 0)
            if leftover > 0:
                leftover -= 1

    # 3. Pad an under-filled row with a transparent spacer so the grid holds.
    shortfall = GRID_COLUMNS - sum(c.colspan for c in resolved)
    if shortfall > 0:
        resolved.append(Card(colspan=shortfall, invisible=True))

    for card in resolved:
        card.width_pct = column_width(card.colspan)

    return resolved


def group_components(components: List) -> List[dict]:
    """
    Clusters a flat component list into the rows the template renders.

    Cards accumulate into grid rows of up to GRID_COLUMNS, terminated early by
    a LineBreak. Everything else buffers onto the two-column content track.
    Sections are grouped recursively and emitted as a single nested row.
    """
    rows: List[dict] = []
    card_block: List = []
    content_buffer: List = []
    content_colspan = 0

    def flush_cards() -> None:
        nonlocal card_block
        if not card_block:
            return

        row_cards: List = []
        row_colspan = 0
        for comp in card_block:
            if isinstance(comp, LineBreak):
                if row_cards:
                    rows.append({"type": "cards", "items": resolve_card_widths(row_cards)})
                    row_cards, row_colspan = [], 0
                continue

            span = comp.colspan if comp.colspan is not None else 1
            if row_colspan + span > GRID_COLUMNS:
                rows.append({"type": "cards", "items": resolve_card_widths(row_cards)})
                row_cards, row_colspan = [], 0

            row_cards.append(comp)
            row_colspan += span

        if row_cards:
            rows.append({"type": "cards", "items": resolve_card_widths(row_cards)})
        card_block = []

    def flush_content() -> None:
        nonlocal content_buffer, content_colspan
        if content_buffer:
            rows.append({"type": "components", "items": content_buffer})
            content_buffer = []
            content_colspan = 0

    for comp in components:
        if isinstance(comp, Card):
            flush_content()
            card_block.append(comp)

        elif isinstance(comp, LineBreak):
            # Inside a run of cards a break splits the row; otherwise it is
            # ordinary vertical space on the content track.
            if card_block:
                card_block.append(comp)
            else:
                content_buffer.append(comp)
                content_colspan += comp.colspan

        elif isinstance(comp, Section):
            flush_content()
            flush_cards()
            rows.append(
                {
                    "type": "section",
                    "title": comp.title,
                    "subtitle": comp.subtitle,
                    "title_align": comp.title_align,
                    "widgets": group_components(comp.widgets),
                }
            )

        else:
            flush_cards()
            if content_colspan + comp.colspan > CONTENT_COLUMNS:
                flush_content()
            content_buffer.append(comp)
            content_colspan += comp.colspan

    flush_cards()
    flush_content()
    return rows
