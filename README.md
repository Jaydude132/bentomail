# BentoMail

> **A Python framework for building professional dashboard-style HTML reports and emails.**

Build beautiful, responsive dashboard-style emails with reusable Python components in minutes.

<div align="center">
  <!-- TODO: Drop your best, most visually striking screenshot of the generated dashboard here -->
  <img src="docs/hero_screenshot.png" alt="BentoMail Hero Image" width="800"/>
</div>

---

## Why BentoMail?

* 📊 **Dashboard-style reports:** Ditch plain text for metric grids, themed charts, and grouped sections.
* 🎨 **Built-in themes:** Ships with polished Dark, Light, Gruvbox, Monokai, and Neutral layouts.
* 🧩 **Component-based API:** Build layouts declaratively using native Python dataclasses.
* 📱 **Outlook-defended layouts:** Fixed-width rendering boundaries completely mitigate classic Microsoft Word/Outlook shrink-wrapping bugs.
* 📈 **Zero-disk charts:** Generates Matplotlib graphs instantly in memory as inline MIME assets.
* ⚡ **Flexible output:** Generate raw HTML strings, extract packed `MIMEMultipart` objects, or dispatch directly over SMTP.

---

## Installation

Install the core, lightweight engine:
```bash
pip install bentomail
```

To enable zero-disk inline chart rendering (installs `matplotlib`):
```bash
pip install bentomail[charts]
```

---

---

## Quick Start

You can generate a fully styled, multi-column layout in under a dozen lines of code.

```python
from bentomail import BentoMailer, themes, colors

# 1. Initialize the engine with a built-in theme
mail = BentoMailer(
    subject="Daily Infrastructure Report",
    theme=themes.GRUVBOX
)

# 2. Build the layout components
mail.create_header(title="Infrastructure Summary", subtitle="Production Cluster")

mail.add_card(title="System CPU", value="34%", color=colors.SUCCESS)
mail.add_card(title="Active Nodes", value="14", color=colors.INFO)
mail.add_card(title="Faults", value="0", color=colors.WARNING)

# 3. Output raw HTML, get the MIME object, or send directly
html_output = mail.compile_dashboard_html()
# msg = mail.as_mime_message()
# mail.send_dashboard()
```

---

## Themes

BentoMail ships with five highly refined elevation themes designed for system operations and data analytics. 

| Theme | Preview | Vibe |
| :--- | :--- | :--- |
| **Neutral** | `<img src="docs/neutral.png" width="200"/>` | Sleek, pure dark-gray, minimal-blue |
| **Gruvbox** | `<img src="docs/gruvbox.png" width="200"/>` | Warm retro, high-contrast terminal |
| **Monokai** | `<img src="docs/monokai.png" width="200"/>` | Retro terminal code editor style |
| **Slate**   | `<img src="docs/slate.png" width="200"/>` | Vibrant dark blue operations panel |
| **Light**   | `<img src="docs/light.png" width="200"/>` | Clean, corporate reporting layout |

---

## Components

Stop wrestling with HTML and inline CSS. BentoMail components handle their own layout proportions, responsive nesting, and semantic coloring automatically.

| Component | Preview | Description |
| :--- | :--- | :--- |
| **Metric Card** | `<img src="docs/card.png" width="250"/>` | Auto-stretching, grid-aligned KPI indicators. |
| **Data Report** | `<img src="docs/report.png" width="250"/>` | Multi-column tables with row-highlighting support. |
| **Polymorphic Alert**| `<img src="docs/alert.png" width="250"/>` | Contextual notices (Critical, Error, Warning, Info, Success). |
| **Line & Bar Charts**| `<img src="docs/chart.png" width="250"/>` | Theme-matching visualization injected directly into the MIME tree. |

---

## Philosophy

BentoMail is designed to make the common case simple while remaining highly customizable. 

New users can generate polished reports in minutes without knowing any HTML, while advanced users can customize themes, colors, and modular layouts to perfectly match their organization’s branding. Layout proportions use an intelligent integer-based `colspan` system, meaning your UI boundaries remain perfectly straight whether you are rendering 2 columns or 4.

---

## Customization

Because themes are built on native frozen dataclasses, advanced users can easily override semantic palettes to match their corporate identity using Python's standard `dataclasses.replace`.

```python
import dataclasses
from bentomail import BentoMailer, themes

# Clone a built-in theme and override specific hex values
custom_theme = dataclasses.replace(
    themes.NEUTRAL,
    bg_color="#000000",
    accent_color="#ff5733",
    success_color="#00ff00"
)

mail = BentoMailer(subject="Custom Alert", theme=custom_theme)
```

---

## Examples

Check the `/examples` directory for complete implementations:
* `basic_alert.py` - Standard status update dispatch.
* `sandbox.py` - Comprehensive layout showcasing every widget in the engine.
* `offline_compilation.py` - Bypassing SMTP to use BentoMail purely as an HTML generation pipeline.

---

## Architecture & API Reference

### 🚀 Key Under-the-Hood Features
1. **Zero-Overhead Dataclasses:** Bypasses heavy schema validation in favor of native Python `dataclasses`. This results in near-instant cold-start execution times—critical for script-runners and scheduled batch orchestrators.
2. **Defended HTML Grids:** Replaces fluid CSS float math with a rigid 850px parent table and integer-based `colspan` boundaries. This guarantees 100% visual parity on volatile rendering engines like Microsoft Outlook.
3. **Decoupled Jinja Templates:** All styling edits (paddings, custom borders, margin spacing) are safely confined within `dashboard.jinja`, eliminating Python runtime regressions.

### Component API Models
All components are exposed via `bentomail.components`. 

*(For advanced subclassing, refer to the source files. The standard interface is fully wrapped by the `BentoMailer` builder methods `add_card()`, `add_report()`, `add_line_chart()`, etc.)*
