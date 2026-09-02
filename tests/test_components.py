import pytest

from bentomail import Section
from bentomail.components import (
    BarChart,
    Card,
    CriticalNotice,
    ErrorNotice,
    Footer,
    FooterLink,
    ImportantNotice,
    InfoNotice,
    Notice,
    Report,
    SuccessNotice,
    WarningNotice,
)


def test_card_defaults_leave_layout_unresolved():
    """A fresh card carries no width until the layout engine resolves one."""
    card = Card()
    assert card.colspan is None
    assert card.width_pct is None
    assert card.invisible is False


def test_report_defaults():
    report = Report()
    assert report.headers == []
    assert report.data == []
    assert report.colspan == 1
    assert report.highlight_row_index is None


def test_report_default_collections_are_not_shared():
    """Mutable defaults must be per-instance, not shared across reports."""
    first, second = Report(), Report()
    first.headers.append("a")
    assert second.headers == []


def test_notice_requires_a_message():
    with pytest.raises(TypeError):
        Notice()


@pytest.mark.parametrize(
    "notice_class, expected_color, expected_header",
    [
        (CriticalNotice, "CRITICAL", "Critical"),
        (ErrorNotice, "ERROR", "Error"),
        (WarningNotice, "WARNING", "Warning"),
        (ImportantNotice, "IMPORTANT", "Important"),
        (SuccessNotice, "SUCCESS", "Success"),
        (InfoNotice, "INFO", "Info"),
    ],
)
def test_notice_severities(notice_class, expected_color, expected_header):
    notice = notice_class(message="text")
    assert notice.color == expected_color
    assert notice.header_text == expected_header
    assert notice.emoji
    assert notice.colspan == 2


# =========================================================================
# --- SECTION WIDGET ENFORCEMENT ---
# =========================================================================
def test_section_forces_reports_to_full_width():
    section = Section(title="S")
    section.add_report(title="R", headers=["a"], data=[["1"]], colspan=1)
    assert section.widgets[0].colspan == 2


def test_section_forces_notices_to_full_width():
    section = Section(title="S")
    section.add_notice(WarningNotice(message="w", colspan=1))
    assert section.widgets[0].colspan == 2


def test_section_forces_charts_to_full_width():
    section = Section(title="S")
    section.add_line_chart(x=[1], y=[2], title="L")
    section.add_bar_chart(categories=["a"], values=[1], title="B")
    section.add_pie_chart(labels=["a"], sizes=[1], title="P")
    assert [w.colspan for w in section.widgets] == [2, 2, 2]


def test_section_cards_keep_their_own_span():
    section = Section(title="S")
    section.add_card(title="A")
    section.add_card(title="B", colspan=2)
    assert [w.colspan for w in section.widgets] == [None, 2]


def test_section_chart_helpers_carry_their_data():
    section = Section(title="S")
    section.add_bar_chart(categories=["x", "y"], values=[1, 2], title="B")
    chart = section.widgets[0]
    assert isinstance(chart, BarChart)
    assert chart.categories == ["x", "y"]
    assert chart.values == [1, 2]


# =========================================================================
# --- BUILDER PIPELINE ---
# =========================================================================
def test_component_pipeline_preserves_order(mailer):
    em = mailer()
    em.add_card(title="My Card", value="10")
    em.add_critical("System Alert")
    assert isinstance(em._components[0], Card)
    assert em._components[1].message == "System Alert"


def test_footer_accepts_dictionaries_and_dataclasses(mailer):
    em = mailer()
    em.create_footer(
        line1="Footer Text",
        links=[
            {"text": "Docs", "url": "https://example.com"},
            FooterLink(text="Repo", url="https://example.com/repo"),
        ],
    )
    assert all(isinstance(link, FooterLink) for link in em.footer_block.links)
    assert [link.text for link in em.footer_block.links] == ["Docs", "Repo"]


def test_builders_accept_prebuilt_dataclasses(mailer):
    """Every builder takes either keyword arguments or a ready-made object."""
    em = mailer()
    em.create_footer(Footer(line1="direct"))
    em.add_card(Card(title="direct", value="1"))
    em.add_report(Report(title="direct"))
    assert em.footer_block.line1 == "direct"
    assert em._components[0].title == "direct"
    assert em._components[1].title == "direct"


def test_report_has_no_header_color_field():
    """
    Removed: it was never rendered, and its hardcoded dark default would have
    clashed with the Light theme had it ever been wired up.
    """
    assert not hasattr(Report(), "header_color")
    with pytest.raises(TypeError):
        Report(header_color="#000000")
