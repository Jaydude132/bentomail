import pytest

from bentomail import Dashboard, Section, themes
from bentomail.components import BarChart, LineChart, PieChart

pytest.importorskip("matplotlib", reason="chart rendering is an optional extra")

from bentomail.chart_renderer import render_chart_to_png  # noqa: E402

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@pytest.mark.parametrize(
    "chart",
    [
        LineChart(title="L", x=[1, 2, 3], y=[4, 5, 6]),
        BarChart(title="B", categories=["a", "b"], values=[1, 2]),
        PieChart(title="P", labels=["a", "b"], sizes=[1, 2]),
    ],
    ids=["line", "bar", "pie"],
)
def test_every_chart_type_renders_to_png(chart):
    data = render_chart_to_png(chart, themes.SLATE)
    assert data.startswith(PNG_MAGIC)


def test_chart_styling_follows_the_theme():
    """Two themes must not produce byte-identical images."""
    chart = LineChart(title="L", x=[1, 2, 3], y=[4, 5, 6])
    assert render_chart_to_png(chart, themes.SLATE) != render_chart_to_png(
        chart, themes.LIGHT
    )


def test_charts_become_inline_cid_references():
    dash = Dashboard()
    dash.add_line_chart(x=[1, 2], y=[3, 4], title="Trend")

    html = dash.to_html()
    assert 'src="cid:chart_' in html
    assert len(dash._inline_images) == 1

    cid = dash._inline_images[0]["Content-ID"].strip("<>")
    assert f"cid:{cid}" in html


def test_inline_images_are_attached_to_the_message():
    dash = Dashboard()
    dash.add_bar_chart(categories=["a"], values=[1], title="B")

    parts = [p.get_content_type() for p in dash.to_mime().walk()]
    assert parts.count("image/png") == 1


def test_charts_nested_in_sections_are_rendered():
    section = Section(title="Capacity")
    section.add_bar_chart(categories=["a", "b"], values=[1, 2], title="Load")

    dash = Dashboard()
    dash.add_section(section)

    assert 'src="cid:chart_' in dash.to_html()
    assert len(dash._inline_images) == 1


def test_recompiling_does_not_accumulate_chart_attachments():
    """
    Regression guard: each compile must replace the previous chart images
    rather than appending a fresh copy of every one.
    """
    dash = Dashboard()
    dash.add_line_chart(x=[1, 2], y=[3, 4], title="Trend")

    for _ in range(3):
        dash.to_html()

    assert len(dash._inline_images) == 1


def test_raw_chart_components_survive_compilation():
    """Compiling swaps charts for image placeholders only in a copy."""
    dash = Dashboard()
    dash.add_line_chart(x=[1, 2], y=[3, 4], title="Trend")
    dash.to_html()
    assert isinstance(dash._components[0], LineChart)
