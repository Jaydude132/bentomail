# Changelog

All notable changes to BentoMail are recorded here.

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-02

First public release.

### Added

- `Dashboard` class owning layout and rendering, independent of any transport.
  `to_html()`, `to_text()`, and `to_mime()` make the engine usable with SES,
  SendGrid, the Graph API, or a plain file.
- `BentoMailer` extends `Dashboard` with addressing and SMTP delivery.
- Plain-text alternative part. Every message is now `multipart/alternative`,
  carrying a text rendering of the same component tree for clients that will
  not display HTML.
- Chart alt text, settable per chart and defaulting to a description built from
  the chart type and title. Charts stand in as their alt text in the plain-text
  part.
- Explicit relay configuration: `smtp_server`, `smtp_port`, `smtp_user`,
  `smtp_pass`, `use_tls`, and `use_ssl` are constructor arguments, with the
  existing environment variables as fallback.
- `branding` flag. Rendered dashboards carry a small credit line at the bottom;
  pass `branding=False` to suppress it.
- `envelope_recipients()` and `cc_list()` for inspecting delivery routing.
- Recursive section nesting. A `Section` inside a `Section` now renders instead
  of raising `AttributeError`.
- Test suite covering the layout engine, rendering, MIME assembly, SMTP
  dispatch, chart rendering, and packaging.

### Fixed

- The Jinja template was missing from built distributions because of a typo in
  the package-data key, so every install failed with `TemplateNotFound`.
- Charts were not genuinely optional. `matplotlib` was imported on every render,
  so a chart-free dashboard failed on an install without the `charts` extra.
- Card widths were resolved onto the caller's own components, so compiling a
  dashboard twice produced a different layout the second time.
- CC addresses were appended to the recipient list, corrupting the `To` header
  on every send after the first. Delivery now uses a separate SMTP envelope.
- `load_dotenv()` ran at import time, mutating the environment of any process
  that merely imported the package. It now runs during `BentoMailer.__init__`
  and can be skipped with `load_env=False`.
- SMTP failures no longer discard the original traceback.
- An empty `Cc` header is no longer emitted when no CC is configured.

### Changed

- The layout engine moved to `bentomail.layout`, replacing two near-identical
  grouping methods with a single recursive function. Grid geometry derives from
  `GRID_COLUMNS` and `GUTTER_PCT` rather than hardcoded percentages.
- `compile_dashboard_html()` and `as_mime_message()` are retained, so existing
  code continues to work.

### Removed

- `Report.header_color`, which was never rendered.
