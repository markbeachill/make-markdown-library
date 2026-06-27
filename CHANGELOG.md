# Changelog

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

### Changed

- Bumped package version to `0.2.0`.
- Replaced the old standalone duplicate implementation with a compatibility launcher that calls the package CLI.
- Expanded tests from 12 to 16 and added coverage for indexing, LiteParse routing, Markdown policy, generated-file skipping, and rebuild reuse.

### Notes

- MarkItDown remains the default converter to avoid surprising existing users.
- LiteParse is optional and can be installed with `make-markdown-library setup liteparse` or the `liteparse`/`all-converters` package extras.
