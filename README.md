# make-markdown-library

Make Markdown Library turns messy folders, files, and ZIP archives into reproducible **AI-readable Markdown libraries** with manifests, JSON/YAML indexes, optional split Markdown files, and MarkItDown/LiteParse converter routing.

- **Documentation site:** https://markbeachill.github.io/make-markdown-library/
- **GitHub repository:** https://github.com/markbeachill/make-markdown-library
- **Latest releases:** https://github.com/markbeachill/make-markdown-library/releases
- **Download installer:** https://github.com/markbeachill/make-markdown-library/releases/download/v0.3.8/make_markdown_library-0.3.8-py3-none-any.whl

```text
sources/                          markdown-library.md
  report.pdf          ─────►      markdown-library-manifest.md
  notes.docx                       markdown-library.index.json
  slides.pptx                     markdown-library-files/   optional
  existing-notes.md                  report.md
  extra.zip                         notes.md
                                    slides.md
```

## Why use it?

- **AI reading packs** — give an assistant one structured Markdown file instead of many attachments.
- **Local-first ingestion** — convert and index project folders on your machine.
- **Reproducibility** — indexes record hashes, converter modes, LiteParse options, fallback notes, and source offsets.
- **Markdown-aware folders** — normal `.md` files are added directly; generated outputs are skipped by default.
- **Rebuilds** — rebuild from a previous index and reuse unchanged sections.
- **Storage/search/version control** — Markdown is plain text, diffable, and easy to archive.

## What’s new in v3.8 / 0.3.8

- User-facing install docs now focus on the install package, not source-code downloads.
- Added an Install Python on Windows page.
- Added an Uninstall page.
- Clarified where the tool is installed: into Python’s user package area, not Downloads and not each document folder.
- GitHub source download is treated as a developer/source-code route, not the main user install route.

v3.1 added the formal processing rules / safety contract and overwrite protections. v3.2 turned those docs into a real browsable site. v3.3 added the GitHub Pages workflow. v3.4 made the published site read like end-user product docs. v3.5 clarified first-time installation. v3.6 polished command examples and code-block usability. v3.7 simplified Windows installation. v3.8 makes installation package-oriented.

## Quick start on Windows

If Python is not installed yet, follow the site guide:

- https://markbeachill.github.io/make-markdown-library/guides/install-python-windows/

Download the wheel installer from the public site or release page, then install it with pip.

```powershell
py -m pip install --user "$env:USERPROFILE\Downloads\make_markdown_library-0.3.8-py3-none-any.whl"
```

Check it works:

```powershell
py -m make_markdown_library --version
```

Run diagnostics:

```powershell
py -m make_markdown_library doctor
```

Build a library:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" --converter auto
```

You install the tool once. After that, point it at any folder you want to convert.

## Quick start on macOS or Linux

Install from a wheel package or source checkout with pip, then run:

```bash
python3 -m make_markdown_library --version
```

Build a library:

```bash
python3 -m make_markdown_library make my-folder -o markdown-library.md --converter auto
```

If the short `make-markdown-library` command works on your PATH, you can use it instead of the longer `python -m make_markdown_library` form.

## Common workflows

### Create a library from a folder

```bash
make-markdown-library make my-folder -o library.md
```

### Also create one Markdown file per source

```bash
make-markdown-library make my-folder -o library.md --individual-files
```

### Use LiteParse as a fallback when MarkItDown returns empty text

```bash
make-markdown-library make my-folder -o library.md --converter auto
```

### Prefer LiteParse for complex/scanned PDFs

```bash
make-markdown-library make my-folder -o library.md --converter auto --liteparse-complexity-check
```

### Tune LiteParse options

```bash
make-markdown-library make my-folder -o library.md --converter hybrid --liteparse-image-mode placeholder --liteparse-ocr-language eng --liteparse-dpi 200
```

### Get machine-readable CLI output

```bash
make-markdown-library make my-folder -o library.md --summary-json
```

### Rebuild from an index

Rebuild the library:

```bash
make-markdown-library rebuild library.index.json
```

Preview the rebuild without writing files:

```bash
make-markdown-library rebuild library.index.json --dry-run
```

## Converter modes

| Mode | Behaviour |
| --- | --- |
| `markitdown` | Use MarkItDown only for supported non-Markdown files. |
| `liteparse` | Use LiteParse only where supported. |
| `auto` | Direct-ingest Markdown/text; try MarkItDown first; fallback to LiteParse when MarkItDown returns empty text; optionally prefer LiteParse for complex PDFs. |
| `hybrid` | Direct-ingest Markdown/text; prefer LiteParse for PDFs/layout-sensitive work; use MarkItDown for broad format coverage and fallback. |

## LiteParse options

LiteParse is optional. Install it only if you need LiteParse converter/fallback features.

```bash
make-markdown-library setup liteparse
```

Available CLI options:

```text
--liteparse-image-mode off|placeholder|markdown|base64
--liteparse-no-links
--liteparse-no-ocr
--liteparse-ocr-language eng
--liteparse-target-pages 1,2,5-8
--liteparse-dpi 150
--liteparse-max-pages 50
--liteparse-password PASSWORD
--liteparse-complexity-check
```

Passwords are never written into index files. The index records only that a password was provided.

## Markdown files already in the folder

Markdown files are first-class inputs. They are not sent through MarkItDown or LiteParse.

Default policy:

```text
--md-policy include
```

This means ordinary Markdown files are included directly, existing generated libraries may be imported, and generated manifests/indexes/split files are skipped.

## Safety rules

The formal behaviour contract is in:

- https://markbeachill.github.io/make-markdown-library/processing-rules/

Important defaults:

- `make` refuses to overwrite existing output files unless `--backup-existing` or `--overwrite` is used.
- `add` and `rebuild` back up existing outputs by default.
- source file and output file cannot be the same file.
- individual split outputs cannot be written directly into the source folder unless explicitly allowed.
- generated split files do not overwrite user-authored Markdown by default.

## Documentation site

The public site is generated from Markdown source in `docs/`.

Build it locally:

```bash
python scripts/build_static_site.py
```

Then open:

```text
site/index.html
```

GitHub Pages deployment is handled by `.github/workflows/publish-site.yml`.

## Development

Install test dependencies and run tests:

```bash
python -m pip install -e .[dev]
```

```bash
pytest -q
```

## Uninstall

Windows:

```powershell
py -m pip uninstall make-markdown-library
```

macOS or Linux:

```bash
python3 -m pip uninstall make-markdown-library
```
