from bentomail import Dashboard, Section, themes
from bentomail.components import WarningNotice

BRANDING_URL = "https://github.com/jaydude132/bentomail"


def test_renders_a_complete_html_document():
    dash = Dashboard(subject="Compilation Test")
    dash.create_header(title="Test Header")
    dash.add_card(title="Test Card", value="99.9%")

    html = dash.to_html()
    assert "<html" in html.lower()
    assert "Test Header" in html
    assert "99.9%" in html


def test_dashboard_defaults():
    dash = Dashboard()
    assert dash.theme == themes.NEUTRAL
    assert dash.branding is True
    assert dash.subject is None
    assert dash._components == []


def test_mailer_inherits_the_dashboard_defaults(mailer):
    em = mailer()
    assert em.theme == themes.NEUTRAL
    assert em.subject == "Test Subject"
    assert em.recipients == ["target@example.com"]


def test_subject_becomes_the_document_title():
    assert (
        "<title>Weekly Report</title>" in Dashboard(subject="Weekly Report").to_html()
    )


def test_theme_colors_reach_the_markup():
    dash = Dashboard(theme=themes.GRUVBOX)
    dash.add_card(title="A", value="1")
    assert themes.GRUVBOX.bg_color in dash.to_html()


def test_semantic_colors_resolve_against_the_theme():
    """A named severity resolves to the active theme's hex value."""
    dash = Dashboard(theme=themes.SLATE)
    dash.add_card(title="A", value="1", color="CRITICAL")
    assert themes.SLATE.critical_color in dash.to_html()


def test_literal_colors_pass_through_untouched():
    dash = Dashboard()
    dash.add_card(title="A", value="1", color="#ABCDEF")
    assert "#ABCDEF" in dash.to_html()


def test_user_content_is_escaped():
    """Autoescape must neutralise markup arriving through component data."""
    dash = Dashboard()
    dash.add_card(title="<script>alert(1)</script>", value="1")
    html = dash.to_html()
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_empty_report_renders_a_placeholder():
    dash = Dashboard()
    dash.add_report(title="Empty", headers=["a"], data=[], colspan=2)
    assert "No data to display." in dash.to_html()


def test_report_tip_and_highlight_render():
    dash = Dashboard(theme=themes.SLATE)
    dash.add_report(
        title="R",
        headers=["a"],
        data=[["1"], ["2"]],
        highlight_row_index=0,
        tip="A helpful note.",
        colspan=2,
    )
    html = dash.to_html()
    assert "A helpful note." in html
    assert themes.SLATE.accent_color in html


def test_nested_section_content_survives_rendering():
    inner = Section(title="Inner Section")
    inner.add_card(title="InnerCard", value="42")
    outer = Section(title="Outer Section")
    outer.add_card(title="OuterCard", value="1")
    outer.widgets.append(inner)

    dash = Dashboard()
    dash.add_section(outer)
    html = dash.to_html()
    for expected in ("Outer Section", "OuterCard", "Inner Section", "InnerCard"):
        assert expected in html


def test_notice_text_renders_inside_a_section():
    section = Section(title="S")
    section.add_notice(WarningNotice(message="Storage is filling up."))
    dash = Dashboard()
    dash.add_section(section)
    assert "Storage is filling up." in dash.to_html()


def test_repeated_compilation_is_stable():
    """
    Regression guard: compiling twice must not shift the layout. Card widths
    were previously resolved onto the caller's own components.
    """
    dash = Dashboard()
    for title in "ABC":
        dash.add_card(title=title, value="1")

    assert dash.to_html() == dash.to_html() == dash.to_html()
    assert 'width="32%"' in dash.to_html()


# =========================================================================
# --- BRANDING ---
# =========================================================================
def test_branding_is_shown_by_default():
    html = Dashboard().to_html()
    assert "Built with" in html
    assert BRANDING_URL in html


def test_branding_can_be_disabled():
    html = Dashboard(branding=False).to_html()
    assert "Built with" not in html
    assert BRANDING_URL not in html


def test_branding_renders_without_a_footer():
    """The credit is independent of whether the user configured a Footer."""
    dash = Dashboard()
    assert dash.footer_block is None
    assert "Built with" in dash.to_html()


def test_branding_does_not_displace_user_footer_content():
    dash = Dashboard()
    dash.create_footer(line1="My own line one", line2="My own line two")
    html = dash.to_html()
    assert "My own line one" in html
    assert "My own line two" in html
    assert html.index("My own line two") < html.index("Built with")


# =========================================================================
# --- SEPARATION FROM TRANSPORT ---
# =========================================================================
def test_dashboard_carries_no_transport_state():
    """A Dashboard renders without any notion of recipients or a relay."""
    dash = Dashboard()
    assert not hasattr(dash, "recipients")
    assert not hasattr(dash, "smtp_server")


def test_dashboard_does_not_read_the_environment(monkeypatch):
    monkeypatch.setenv("SMTP_SERVER", "should-not-be-read.example.com")
    dash = Dashboard()
    dash.add_card(title="A", value="1")
    assert "should-not-be-read" not in dash.to_html()


def test_compile_dashboard_html_alias_still_works():
    dash = Dashboard()
    dash.add_card(title="A", value="1")
    assert dash.compile_dashboard_html() == dash.to_html()
