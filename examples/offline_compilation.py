# Author: Jason Marencic
# June 2, 2026

"""
Using BentoMail purely as an HTML generation pipeline.

A Dashboard has no notion of recipients or SMTP, so it can be handed to any
delivery mechanism: a transactional email API, a static file, or a web view.
Run this file to write both renderings of the same report to disk.
"""

from pathlib import Path

from bentomail import Dashboard, themes

OUTPUT_DIR = Path(__file__).parent / "output"


def build_report() -> Dashboard:
    dash = Dashboard(theme=themes.SLATE, subject="Nightly Build Report")

    dash.create_header(
        description="CONTINUOUS INTEGRATION",
        title="Nightly Build Report",
        subtitle="main @ 4f2a1c9",
    )

    dash.add_card(title="Build", value="Passing", label="12m 04s", color="SUCCESS")
    dash.add_card(title="Tests", value="1,284", label="3 skipped", color="INFO")
    dash.add_card(title="Coverage", value="91.2%", label="+0.4%", color="SUCCESS")
    dash.add_card(
        title="Warnings", value="7", label="all non-blocking", color="WARNING"
    )

    dash.add_report(
        title="Slowest Suites",
        headers=["Suite", "Duration", "Tests"],
        data=[
            ["integration.api", "4m 12s", "318"],
            ["integration.db", "2m 55s", "204"],
            ["unit.layout", "0m 48s", "412"],
        ],
        highlight_row_index=0,
        colspan=2,
    )

    dash.add_info("Artifacts are retained for 30 days.")
    return dash


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    dashboard = build_report()

    # The HTML body, ready to hand to any provider.
    html_path = OUTPUT_DIR / "report.html"
    html_path.write_text(dashboard.to_html(), encoding="utf-8")

    # The plain-text alternative, as a client refusing HTML would see it.
    text_path = OUTPUT_DIR / "report.txt"
    text_path.write_text(dashboard.to_text(), encoding="utf-8")

    # A MIME body with the inline images already attached, but no routing
    # headers. Useful for providers that accept a raw message.
    message = dashboard.to_mime()

    print(f"HTML  -> {html_path}")
    print(f"Text  -> {text_path}")
    print(f"MIME  -> {message.get_content_type()}")


if __name__ == "__main__":
    main()
