import sys
from pathlib import Path

import jinja2
import pytest

import bentomail
from bentomail import Dashboard, Section

TEMPLATE_NAME = "dashboard.jinja"


def test_template_is_reachable_through_the_package_loader():
    """
    The renderer locates the template with a PackageLoader, so this fails
    whenever package-data stops shipping the templates directory.
    """
    env = jinja2.Environment(loader=jinja2.PackageLoader("bentomail", "templates"))
    assert env.get_template(TEMPLATE_NAME) is not None


def test_template_sits_inside_the_installed_package():
    template = Path(bentomail.__file__).parent / "templates" / TEMPLATE_NAME
    assert template.is_file()
    assert template.stat().st_size > 0


def test_version_is_exposed():
    assert bentomail.__version__


def test_public_names_are_importable():
    for name in bentomail.__all__:
        assert hasattr(bentomail, name), name


# =========================================================================
# --- OPTIONAL CHART DEPENDENCY ---
# =========================================================================
@pytest.fixture
def without_matplotlib(monkeypatch):
    """Makes `import matplotlib` fail, simulating an install without extras."""
    monkeypatch.setitem(sys.modules, "matplotlib", None)


def test_chart_free_dashboard_renders_without_matplotlib(without_matplotlib):
    """
    The charts extra is optional, so a dashboard that uses no charts must
    never reach for matplotlib.
    """
    dash = Dashboard(subject="Ops")
    dash.create_header(title="Service Health")
    dash.add_card(title="Uptime", value="99.98%")
    dash.add_report(title="Traffic", headers=["Svc"], data=[["api"]])
    dash.add_success("All good.")

    assert "99.98%" in dash.to_html()


def test_chart_free_dashboard_builds_mime_without_matplotlib(without_matplotlib):
    dash = Dashboard(subject="Ops")
    dash.add_card(title="Uptime", value="99.98%")
    assert dash.to_mime().get_content_type() == "multipart/related"


def test_requesting_a_chart_without_matplotlib_explains_the_extra(without_matplotlib):
    dash = Dashboard()
    dash.add_line_chart(x=[1, 2], y=[3, 4], title="Trend")

    with pytest.raises(ImportError, match=r"bentomail\[charts\]"):
        dash.to_html()


def test_chart_nested_in_a_section_is_still_detected(without_matplotlib):
    section = Section(title="Capacity")
    section.add_bar_chart(categories=["a"], values=[1], title="Load")

    dash = Dashboard()
    dash.add_section(section)

    with pytest.raises(ImportError):
        dash.to_html()


def test_chart_detection_walks_nested_sections():
    dash = Dashboard()
    assert dash._has_charts(dash._components) is False

    inner = Section(title="Inner")
    inner.add_line_chart(x=[1], y=[2], title="L")
    outer = Section(title="Outer")
    outer.widgets.append(inner)

    assert dash._has_charts([outer]) is True
