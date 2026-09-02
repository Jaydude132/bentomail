from bentomail.components import Card, LineBreak, Report, Section
from bentomail.layout import (
    GRID_COLUMNS,
    column_width,
    equal_width,
    group_components,
    resolve_card_widths,
)


def cards(*colspans):
    """Builds a row of cards from a sequence of colspan values."""
    return [Card(title=f"C{i}", colspan=c) for i, c in enumerate(colspans)]


# =========================================================================
# --- WIDTH ARITHMETIC ---
# =========================================================================
def test_column_width_matches_the_four_column_grid():
    widths = [column_width(n) for n in range(1, GRID_COLUMNS + 1)]
    assert widths == ["23.5%", "49%", "74.5%", "100%"]


def test_equal_width_splits_a_row_evenly():
    assert [equal_width(n) for n in range(1, 5)] == ["100%", "49%", "32%", "23.5%"]


def test_equal_rows_and_their_gutters_total_one_hundred_percent():
    """
    A row plus its gutters must fill the width exactly. Rows never exceed
    GRID_COLUMNS cards, since the grouper splits them before that.
    """
    for count in range(1, GRID_COLUMNS + 1):
        width = float(equal_width(count).rstrip("%"))
        gutters = (count - 1) * 2.0
        assert round(width * count + gutters, 6) == 100.0


def test_explicit_spans_and_their_gutters_also_total_one_hundred_percent():
    for spans in ([1, 1, 1, 1], [2, 2], [3, 1], [4]):
        total = sum(float(column_width(s).rstrip("%")) for s in spans)
        gutters = (len(spans) - 1) * 2.0
        assert round(total + gutters, 6) == 100.0


# =========================================================================
# --- CARD WIDTH RESOLUTION ---
# =========================================================================
def test_unassigned_cards_share_the_row_equally():
    resolved = resolve_card_widths(cards(None, None, None))
    assert [c.width_pct for c in resolved] == ["32%"] * 3
    assert [c.colspan for c in resolved] == [1, 1, 1]


def test_explicit_colspans_map_to_grid_widths():
    resolved = resolve_card_widths(cards(3, 1))
    assert [c.width_pct for c in resolved] == ["74.5%", "23.5%"]


def test_unassigned_cards_absorb_the_remaining_columns():
    resolved = resolve_card_widths(cards(2, None, None))
    assert [c.colspan for c in resolved] == [2, 1, 1]


def test_underfilled_row_gains_an_invisible_spacer():
    resolved = resolve_card_widths(cards(2))
    assert len(resolved) == 2
    assert resolved[-1].invisible is True
    assert resolved[-1].colspan == 2


def test_unassigned_rows_spread_instead_of_gaining_a_spacer():
    """
    Padding applies only to rows using explicit colspans. A row of cards that
    never declared a span is simply divided evenly, however few there are.
    """
    resolved = resolve_card_widths(cards(None))
    assert len(resolved) == 1
    assert resolved[0].width_pct == "100%"


def test_full_row_gains_no_spacer():
    resolved = resolve_card_widths(cards(2, 2))
    assert len(resolved) == 2
    assert not any(c.invisible for c in resolved)


def test_resolution_leaves_the_caller_cards_untouched():
    """
    Resolution must work on copies. Reusing a dashboard would otherwise
    compile a different layout the second time around.
    """
    original = cards(None, None, None)
    resolve_card_widths(original)
    assert [c.colspan for c in original] == [None, None, None]
    assert [c.width_pct for c in original] == [None, None, None]


# =========================================================================
# --- ROW GROUPING ---
# =========================================================================
def test_cards_overflow_into_a_second_row():
    rows = group_components([Card(title=str(i)) for i in range(5)])
    assert [r["type"] for r in rows] == ["cards", "cards"]
    assert len(rows[0]["items"]) == 4
    # A lone card with no explicit colspan simply spans the full width.
    assert len(rows[1]["items"]) == 1
    assert rows[1]["items"][0].width_pct == "100%"


def test_explicit_colspans_wrap_when_the_row_is_full():
    rows = group_components(cards(3, 3))
    assert len(rows) == 2


def test_linebreak_ends_a_card_row_early():
    components = [Card(title="A"), Card(title="B"), LineBreak(), Card(title="C")]
    rows = group_components(components)
    assert [len(r["items"]) for r in rows] == [2, 1]
    assert [c.width_pct for c in rows[0]["items"]] == ["49%", "49%"]


def test_content_components_share_a_two_column_row():
    rows = group_components(
        [Report(title="A", colspan=1), Report(title="B", colspan=1)]
    )
    assert len(rows) == 1
    assert rows[0]["type"] == "components"
    assert len(rows[0]["items"]) == 2


def test_wide_content_component_takes_its_own_row():
    rows = group_components(
        [Report(title="A", colspan=2), Report(title="B", colspan=1)]
    )
    assert [len(r["items"]) for r in rows] == [1, 1]


def test_cards_and_content_do_not_share_a_row():
    rows = group_components([Card(title="A"), Report(title="R", colspan=2)])
    assert [r["type"] for r in rows] == ["cards", "components"]


def test_sections_become_their_own_row_with_grouped_widgets():
    section = Section(title="Capacity")
    section.add_card(title="A")
    section.add_card(title="B")
    section.add_report(title="R", headers=["h"], data=[["v"]])

    rows = group_components([section])
    assert len(rows) == 1
    assert rows[0]["type"] == "section"
    assert rows[0]["title"] == "Capacity"
    assert [w["type"] for w in rows[0]["widgets"]] == ["cards", "components"]


def test_sections_group_recursively():
    inner = Section(title="Inner")
    inner.add_card(title="I")
    outer = Section(title="Outer")
    outer.widgets.append(inner)

    rows = group_components([outer])
    nested = rows[0]["widgets"]
    assert [w["type"] for w in nested] == ["section"]
    assert nested[0]["title"] == "Inner"


def test_grouping_the_same_components_twice_gives_the_same_layout():
    """
    Compiling a dashboard more than once must not drift. This is the
    regression guard for widths being resolved onto shared components.
    """
    components = [Card(title="A"), Card(title="B"), Card(title="C")]

    first = group_components(components)
    second = group_components(components)

    assert [c.width_pct for c in first[0]["items"]] == [
        c.width_pct for c in second[0]["items"]
    ]
    assert all(c.colspan is None for c in components)
