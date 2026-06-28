# Changelog

## 0.3.7

### Changed

- Simplified the Windows install path: the default guide now uses `py -m pip install .` instead of a virtual environment.
- Explained that the tool is installed once and can then be run against any document folder.
- Removed the implication that users should keep or work from the Downloads folder after installation.
- Moved virtual environment instructions into an advanced optional section.
- Updated README, getting started docs, Windows install docs, generated site pages, and `llms.txt`.
- Updated package version to `0.3.7`.

## 0.3.6

### Changed

- Improved the public documentation code blocks so examples wrap instead of forcing horizontal scrolling.
- Copy buttons now appear only on useful single-command shell/PowerShell blocks, not on text output, JSON, file trees, or multi-command explanation blocks.
- Reworked the Windows install guide so every command is explained and shown separately.
- Reworked Getting Started, Troubleshooting, CLI Reference, Processing Rules, and index docs to avoid grouping alternative commands in one copyable block.
- Updated package version to `0.3.6`.

### Fixed

- Fixed malformed Markdown/code fencing on the Windows install page that made later instructions render inside code boxes.
- Fixed a typo in the Windows first-library example path.

## 0.3.5

### Added

- Added `docs/guides/windows-install.md` with a step-by-step Windows install path from ZIP download to first build.
- Added the Windows install guide to the generated public HTML docs and optional MkDocs navigation.

### Changed

- Updated package version to `0.3.5`.
- Reworked Getting Started so `pip install -e .` is introduced only after the user has downloaded and unzipped the repository and opened a shell in the extracted folder.
- Expanded README quick start with separate Windows and macOS/Linux setup commands.

## 0.3.4

### Added

- Added real project links to the generated HTML site: deployed documentation URL, GitHub repository URL, issues URL, and download ZIP URL.
- Added `site.config.json` for public site, repository, issues, and download links.

### Changed

- Updated package version to `0.3.4`.
- Removed self-referential documentation build/deployment guide pages and per-page Markdown/source links from the public generated site navigation.
- Updated the generated site homepage and top navigation with real download/source links.
- Moved static-site and GitHub Pages maintenance guidance to the repository README/source docs rather than public site navigation.

## 0.3.3

### Added

- Added a ready-to-use GitHub Pages workflow at `.github/workflows/publish-site.yml`.
- Added `docs/guides/github-pages.md` with setup, manual deploy, local preview, and MkDocs alternative instructions.
- Added the GitHub Pages guide to the static HTML docs, MkDocs navigation, README, and `llms.txt`.

### Changed

- Updated package version to `0.3.3`.
- The Pages workflow now rebuilds `site/` from `docs/` before deployment instead of only publishing the checked-in `site/` folder.
- The Pages workflow triggers on docs, generator, site, `llms.txt`, `mkdocs.yml`, and workflow changes.


## 0.3.2

### Added

- Added a LiteParse-inspired multi-page static HTML documentation site under `site/`.
- Added `scripts/build_static_site.py`, a dependency-free generator that converts the Markdown docs in `docs/` into browsable HTML pages.
- Added `docs/guides/static-html-site.md` to explain Markdown source docs versus generated HTML pages.
- Added HTML pages for overview, getting started, processing rules, CLI reference, output reference, troubleshooting, and all guide pages.
- Added static documentation assets for sidebar navigation, right-hand page outline, copy buttons, theme toggle, and local search filtering.

### Changed

- Updated package version to `0.3.2`.
- Expanded the Markdown source docs with more detail so the generated site has real multi-page documentation instead of a single landing page with links to `.md` files.
- Replaced the old single-page `site/index.html` links to Markdown files with real HTML documentation links.
- Updated README, MkDocs navigation, and `llms.txt` to describe the HTML documentation site.

## 0.3.1


### Added

- Added `docs/processing-rules.md`, a formal step-by-step processing rules and safety contract.
- Added `--backup-existing`, `--overwrite`, `--clean-individual-dir`, `--overwrite-individual`, and `--allow-individual-in-source` safety controls for `make`.
- Added rebuild safety controls: default backup behaviour plus `--no-backup-existing` and `--overwrite`.
- Added automatic backups for `add` by default, with `--no-backup-existing` for advanced users.
- Added tests for overwrite refusal, backup creation, source/output path refusal, individual directory safety, individual Markdown collision protection, and custom split directory exclusion.

### Changed

- Updated package version to `0.3.1`.
- `make` now refuses to overwrite existing library, manifest, and index outputs unless the user explicitly selects overwrite or backup behaviour.
- `add` and `rebuild` now back up existing outputs by default before modifying them.
- Custom individual output directories are excluded from source scanning during the same run.
- Individual split outputs no longer overwrite user-authored Markdown files by default; numbered filenames are used instead.
- The GUI now uses backup-before-replace behaviour when rebuilding an existing output.

### Fixed

- Refuses `source file == output file`, preventing accidental source destruction.
- Refuses writing individual Markdown files directly into the source folder unless explicitly allowed.
- Old generated split files can now be cleaned safely with `--clean-individual-dir` without deleting user-authored Markdown.

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
