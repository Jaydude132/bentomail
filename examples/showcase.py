# Author: Jason Marencic
# June 2, 2026

"""
Every widget in the engine, in one dashboard.

Running this file writes the rendered HTML and its plain-text alternative to
examples/output/. Pass --theme to try a different palette:

    python examples/showcase.py --theme GRUVBOX
"""

import argparse
from pathlib import Path

from bentomail import Dashboard, Section, themes
from bentomail.components import (
    CriticalNotice,
    ErrorNotice,
    ImportantNotice,
    InfoNotice,
    SuccessNotice,
    WarningNotice,
)

OUTPUT_DIR = Path(__file__).parent / "output"

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAILY_REQUESTS = [6.9, 7.2, 7.4, 7.6, 7.3, 5.9, 5.9]
SERVICES = ["api-gateway", "auth", "search", "checkout", "media"]
SERVICE_P99 = [120, 96, 210, 143, 305]


def build_showcase(theme) -> Dashboard:
    dash = Dashboard(theme=theme, subject=f"BentoMail Showcase ({theme.name})")

    # --- Header and hero ---
    dash.create_header(
        description="PLATFORM OPERATIONS  ·  WEEKLY DIGEST",
        title="Service Health Report",
        subtitle="Week 35",
    )
    dash.create_hero(
        badge="ALL SYSTEMS OPERATIONAL",
        title="99.98% uptime across 14 services",
        description=(
            "Traffic grew 12.4% week over week with no customer-facing incidents. "
            "Median API latency improved to 84 ms following Tuesday's cache rollout."
        ),
    )

    # --- Card grid: four unassigned cards resolve to equal widths ---
    dash.add_card(
        title="Uptime", value="99.98%", label="SLO target 99.90%", color="SUCCESS"
    )
    dash.add_card(title="Total Requests", value="48.2M", label="+12.4%", color="INFO")
    dash.add_card(
        title="p50 Latency", value="84 ms", label="19 ms faster", color="SUCCESS"
    )
    dash.add_card(
        title="Error Rate", value="0.04%", label="Budget 0.10%", color="SUCCESS"
    )

    # --- Explicit colspans: a wide card beside a narrow one ---
    dash.add_card(
        title="Monthly Availability", value="99.99%", label="Rolling 30 days", colspan=3
    )
    dash.add_card(title="Open Incidents", value="0", colspan=1, color="INFO")

    # --- Charts render inline as CID-attached images ---
    dash.add_line_chart(
        x=WEEKDAYS, y=DAILY_REQUESTS, title="Daily Request Volume", y_label="Millions"
    )

    # --- Two half-width tables share one row ---
    dash.add_report(
        title="Traffic by Service",
        headers=["Service", "Requests", "p99"],
        data=[
            ["api-gateway", "21.4M", "120 ms"],
            ["auth", "9.8M", "96 ms"],
            ["search", "7.2M", "210 ms"],
        ],
        highlight_row_index=0,
        colspan=1,
    )
    dash.add_report(
        title="Slowest Endpoints",
        headers=["Endpoint", "p99"],
        data=[
            ["/v2/media/transcode", "305 ms"],
            ["/v2/search/suggest", "210 ms"],
            ["/v2/checkout/quote", "143 ms"],
        ],
        colspan=1,
    )

    # --- Every notice severity ---
    dash.add_notice(
        CriticalNotice(message="Primary database failover triggered in us-east-1.")
    )
    dash.add_notice(
        ErrorNotice(message="Nightly reconciliation job exited with code 1.")
    )
    dash.add_notice(WarningNotice(message="Object storage crosses 80% in three weeks."))
    dash.add_notice(
        ImportantNotice(message="Certificate rotation scheduled for September 20.")
    )
    dash.add_notice(
        SuccessNotice(message="Cache rollout completed across all regions.")
    )
    dash.add_notice(InfoNotice(message="Read replicas added in eu-west-1 on Thursday."))

    # --- A section groups its own widgets inside a bordered panel ---
    capacity = Section(title="Capacity & Cost", subtitle="Rolling 30-day projection")
    capacity.add_card(
        title="Compute Spend", value="$18.4K", label="Under forecast", color="SUCCESS"
    )
    capacity.add_card(
        title="Storage Used", value="72%", label="of 40 TB", color="WARNING"
    )
    capacity.add_card(
        title="Peak Headroom", value="2.8x", label="above peak", color="INFO"
    )
    capacity.add_bar_chart(
        categories=SERVICES,
        values=SERVICE_P99,
        title="p99 Latency by Service",
        y_label="ms",
    )
    capacity.add_report(
        title="Growth Forecast",
        headers=["Resource", "Now", "In 30 days"],
        data=[
            ["Object storage", "28.8 TB", "33.1 TB"],
            ["Compute hours", "4,120", "4,610"],
        ],
        tip="Forecasts assume the current seven-day growth rate holds.",
    )
    capacity.add_notice(
        WarningNotice(message="Schedule a storage tier review before September 20.")
    )
    dash.add_section(capacity)

    # --- Pie charts round out the chart types ---
    dash.add_pie_chart(
        labels=SERVICES,
        sizes=[21.4, 9.8, 7.2, 5.1, 4.7],
        title="Request Share by Service",
    )

    dash.create_footer(
        line1="Generated automatically by the platform reporting pipeline.",
        line2="Questions? Reach the platform team in #ops-support.",
        links=[
            {"text": "Runbook", "url": "https://example.com/runbook"},
            {"text": "Dashboards", "url": "https://example.com/dashboards"},
        ],
    )
    return dash


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--theme",
        default="SLATE",
        choices=["LIGHT", "NEUTRAL", "SLATE", "GRUVBOX", "MONOKAI"],
    )
    args = parser.parse_args()

    theme = getattr(themes, args.theme)
    dashboard = build_showcase(theme)

    OUTPUT_DIR.mkdir(exist_ok=True)
    slug = f"showcase_{theme.name.lower()}"
    (OUTPUT_DIR / f"{slug}.html").write_text(dashboard.to_html(), encoding="utf-8")
    (OUTPUT_DIR / f"{slug}.txt").write_text(dashboard.to_text(), encoding="utf-8")

    print(f"Wrote {slug}.html and {slug}.txt to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
