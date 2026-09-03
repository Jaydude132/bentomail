# BentoMail

[![CI](https://github.com/jaydude132/bentomail/actions/workflows/ci.yml/badge.svg)](https://github.com/jaydude132/bentomail/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/bentomail.svg)](https://pypi.org/project/bentomail/)
[![Python](https://img.shields.io/pypi/pyversions/bentomail.svg)](https://pypi.org/project/bentomail/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Build dashboard-style HTML emails in Python, without writing a line of HTML.**

Metric grids, themed charts, data tables, and status notices — assembled from
plain dataclasses and rendered into email that survives Outlook.

<div align="center">
  <img src="https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_slate.png" alt="A BentoMail dashboard email in the Slate theme" width="700"/>
</div>

---

## Why BentoMail?

* 📊 **Dashboard layouts, not plain text.** Metric card grids, inline charts, tables, and grouped sections.
* 🧩 **Components, not markup.** Build the layout declaratively; the engine resolves the grid.
* 📐 **Outlook-defended.** A fixed 850px parent table and integer `colspan` boundaries sidestep the classic Word-engine shrink-wrap bugs.
* 🎨 **Five built-in themes,** each a frozen dataclass you can clone and override.
* 📈 **Charts with no temp files.** Matplotlib figures are rendered in memory and attached as inline CID images.
* ✉️ **Always multipart.** Every message carries a plain-text alternative alongside the HTML.
* ⚡ **Light footprint.** Jinja2 and python-dotenv. Charts are an optional extra.

---

## Installation

```bash
pip install bentomail
```

Inline chart rendering is optional, since it pulls in matplotlib:

```bash
pip install "bentomail[charts]"
```

---

## Quick Start

```python
from bentomail import BentoMailer, themes

mail = BentoMailer(
    recipients=["team@example.com"],
    subject="Daily Infrastructure Report",
    theme=themes.GRUVBOX,
)

mail.create_header(title="Infrastructure Summary", subtitle="Production Cluster")

# Severity names resolve against the active theme's palette.
mail.add_card(title="System CPU", value="34%", color="SUCCESS")
mail.add_card(title="Active Nodes", value="14", color="INFO")
mail.add_card(title="Faults", value="0", color="WARNING")

mail.send_dashboard()
```

Four unassigned cards fill a row and wrap automatically. Pass `colspan` when you
want explicit proportions.

---

## Two ways to use it

`Dashboard` builds and renders. `BentoMailer` extends it with addressing and SMTP.
If you deliver through SES, SendGrid, or the Graph API, you only need the former —
it never touches SMTP config or your environment.

```python
from bentomail import Dashboard, themes

dash = Dashboard(theme=themes.SLATE, subject="Weekly Report")
dash.add_card(title="Uptime", value="99.98%", color="SUCCESS")

html = dash.to_html()  # markup for your own transport
text = dash.to_text()  # the plain-text alternative
msg = dash.to_mime()  # MIME body with inline images, no routing headers
```

```python
from bentomail import BentoMailer

mail = BentoMailer(recipients=["team@example.com"], subject="Weekly Report")
mail.add_card(title="Uptime", value="99.98%", color="SUCCESS")

msg = mail.as_mime_message()  # fully addressed
mail.send_dashboard()  # or dispatch it
```

Relay settings come from constructor arguments first, then the environment
(`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SENDER_EMAIL`), which
can live in a `.env` file. TLS and SSL are inferred from ports 587 and 465
unless you set `use_tls` or `use_ssl` yourself.

---

## Themes

| Theme | Preview |
| :--- | :--- |
| **Slate** — vibrant dark blue operations panel | <img src="https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_slate_compact.png" width="320"/> |
| **Neutral** — pure dark gray, minimal accent | <img src="https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_neutral_compact.png" width="320"/> |
| **Light** — clean corporate reporting layout | <img src="https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_light_compact.png" width="320"/> |
| **Gruvbox** — warm retro, high-contrast terminal | <img src="https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_gruvbox_compact.png" width="320"/> |
| **Monokai** — retro code-editor palette | <img src="https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_monokai_compact.png" width="320"/> |

Full-height dashboards:
[Slate](https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_slate.png) ·
[Neutral](https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_neutral.png) ·
[Light](https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_light.png) ·
[Gruvbox](https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_gruvbox.png) ·
[Monokai](https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/theme_monokai.png)

---

## Components

| Component | Preview |
| :--- | :--- |
| **Metric cards** — auto-balancing KPI grid | <img src="https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/component_cards.png" width="320"/> |
| **Data reports** — tables with row highlighting | <img src="https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/component_report.png" width="320"/> |
| **Status notices** — six severities | <img src="https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/component_notices.png" width="320"/> |
| **Charts** — line, bar, and pie, theme-matched | <img src="https://raw.githubusercontent.com/jaydude132/bentomail/main/screenshots/png/component_charts.png" width="320"/> |

Sections group widgets inside a bordered panel and can nest:

```python
from bentomail import BentoMailer, Section
from bentomail.components import WarningNotice

mail = BentoMailer(recipients=["team@example.com"], subject="Capacity Review")

capacity = Section(title="Capacity & Cost", subtitle="Rolling 30-day projection")
capacity.add_card(title="Storage Used", value="72%", color="WARNING")
capacity.add_bar_chart(categories=["api", "auth"], values=[120, 96], title="p99")
capacity.add_notice(WarningNotice(message="Storage crosses 80% in three weeks."))

mail.add_section(capacity)
```

---

## Customization

Themes are frozen dataclasses, so cloning one is standard library work:

```python
import dataclasses
from bentomail import BentoMailer, themes

house_style = dataclasses.replace(
    themes.NEUTRAL,
    bg_color="#000000",
    accent_color="#ff5733",
    success_color="#00ff00",
)

mail = BentoMailer(subject="Custom Alert", theme=house_style)
```

---

## Attribution

Rendered dashboards carry a small "Built with BentoMail" line at the very
bottom, below your own footer. To turn it off:

```python
from bentomail import BentoMailer

mail = BentoMailer(
    recipients=["team@example.com"],
    subject="Weekly Report",
    branding=False,
)
```

---

## Examples

The `examples/` directory holds runnable scripts:

* `basic_alert.py` — a short status email. Prints by default; `--send` dispatches it.
* `showcase.py` — every widget in one dashboard. `--theme` switches palette.
* `offline_compilation.py` — using BentoMail purely as an HTML pipeline, no SMTP.

---

## How it works

1. **Components are plain dataclasses.** No schema validation layer, so import
   and construction stay fast — which matters for cron-driven report jobs.
2. **The layout engine resolves a four-column grid.** Cards you leave unsized
   spread evenly across their row, so three cards become three equal columns.
   Cards given an explicit `colspan` keep the proportion you asked for, and a
   row left partly filled is padded with a transparent spacer so the grid holds.
   Rows wrap at four columns. Every width comes from a single formula.
3. **Rendering is confined to `dashboard.jinja`.** Styling changes live in the
   template, not in Python.
4. **Messages are `multipart/alternative`.** The plain-text part is generated
   from the same component tree, with charts represented by their alt text.

---

## License

MIT. See [LICENSE](LICENSE).
