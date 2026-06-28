# Changelog

## 0.3.0

### Added

- Added workflow-first documentation in `docs/`.
- Added `llms.txt` for agent-readable project guidance.
- Added LiteParse options for image mode, link extraction, OCR, OCR language, target pages, DPI, max pages, and protected documents.
- Added `--liteparse-complexity-check` for optional PDF complexity routing via `lit is-complex` when available.
- Added JSON/YAML index schema `1.1` with converter options, output statistics, fallback information, complexity information, and Markdown metadata.
- Added CLI output modes: `--verbose`, `--quiet`, and `--summary-json`.
- Added `rebuild --dry-run` to report what would rebuild, skip, or be removed before writing files.
- Added deeper `doctor` checks for `lit` CLI, OCR-related tooling, LibreOffice, ImageMagick, Tkinter, MarkItDown, LiteParse, and PyYAML.
- Added tests for LiteParse options, complexity routing, index schema `1.1`, and rebuild dry-run planning.

### Changed

- Updated package version to `0.3.0`.
- Improved `auto` and `hybrid` routing. Hybrid now prefers LiteParse for PDFs while keeping MarkItDown for broad format coverage.
- Improved index reproducibility by recording LiteParse option values and output counts.
- Improved direct Markdown metadata with explicit direct-Markdown converter naming and Markdown policy fields.
- Expanded tests to 20 passing tests.

### Fixed

- Empty converter output is now represented as structured fallback/skipped metadata in the index.
- Password values passed to LiteParse are not written into JSON/YAML indexes.

## 0.2.1

### Changed

- In `auto`/`hybrid` converter mode, MarkItDown is tried first and LiteParse is used as a fallback when MarkItDown returns empty or whitespace-only output for a LiteParse-supported file.
- Documented the terminal output and generated files.

## 0.2.0

Implemented the improvement plan from the repository review paper.

### Added

- Pluggable conversion layer with `markitdown`, `liteparse`, `auto`, and `hybrid` modes.
- Optional LiteParse converter using Markdown output.
- Direct reading for Markdown and simple text sources.
- Markdown policy options: `include`, `import-libs`, and `skip`.
- Default skipping for generated manifests, indexes, and split Markdown files.
- JSON index output by default, with optional YAML or both.
- Full SHA-256 hashes in source sections and index files.
- Converter name/version metadata in source sections and manifests.
- Library-section line and character offsets in the index.
- `doctor` command for dependency and system-tool diagnostics.
- `setup` command for MarkItDown, LiteParse, YAML, or all converter extras.
- `rebuild` command that reuses unchanged sections from a previous JSON index.
- GUI controls for converter mode, Markdown policy, index format, and LiteParse installation.

### Notes

- MarkItDown remains the default converter to avoid surprising existing users.
- LiteParse is optional and can be installed with `make-markdown-library setup liteparse` or the `liteparse`/`all-converters` package extras.
