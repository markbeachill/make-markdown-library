# make-markdown-library

Make Markdown Library turns messy folders, files, and ZIP archives into reproducible **AI-readable Markdown libraries** with manifests, JSON/YAML indexes, optional split Markdown files, and MarkItDown/LiteParse converter routing.

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

## What’s new in v3 / 0.3.0

- Workflow-first documentation in `docs/`, modelled after clean developer docs.
- `llms.txt` for coding agents and LLM-assisted workflows.
- LiteParse option flags for image mode, links, OCR, OCR language, target pages, DPI, max pages, and passwords.
- Optional PDF complexity routing with `--liteparse-complexity-check`.
- Index schema `1.1` with converter options, output statistics, fallback metadata, complexity metadata, and Markdown metadata.
- CLI output modes: normal summary, `--verbose`, `--quiet`, and `--summary-json`.
- Rebuild dry-run: `make-markdown-library rebuild markdown-library.index.json --dry-run`.
- Improved `doctor` diagnostics, including the `lit` CLI and OCR-related tooling.

## Quick start

```bash
pip install -e .
make-markdown-library make sources -o markdown-library.md --converter auto
```

Use the GUI:

```bash
python -m make_markdown_library gui
```

Check optional tools:

```bash
make-markdown-library doctor
make-markdown-library setup liteparse
```

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
make-markdown-library make my-folder -o library.md \
  --converter auto \
  --liteparse-complexity-check
```

### Tune LiteParse options

```bash
make-markdown-library make my-folder -o library.md \
  --converter hybrid \
  --liteparse-image-mode placeholder \
  --liteparse-ocr-language eng \
  --liteparse-dpi 200 \
  --liteparse-target-pages 1,2,5-8
```

### Get machine-readable CLI output

```bash
make-markdown-library make my-folder -o library.md --summary-json
```

### Rebuild from an index

```bash
make-markdown-library rebuild library.index.json
make-markdown-library rebuild library.index.json --dry-run
```

## Converter modes

| Mode | Behaviour |
| --- | --- |
| `markitdown` | Use MarkItDown only for supported non-Markdown files. |
| `liteparse` | Use LiteParse only where supported. |
| `auto` | Direct-ingest Markdown/text; try MarkItDown first; fallback to LiteParse when MarkItDown returns empty text; optionally prefer LiteParse for complex PDFs. |
| `hybrid` | Direct-ingest Markdown/text; prefer LiteParse for PDFs/layout-sensitive work; use MarkItDown for broad format coverage and fallback. |

MarkItDown exposes converted text through its result object, so Make Markdown Library treats an empty or whitespace-only conversion result as “no readable text.” In `auto`/`hybrid` modes, LiteParse can then kick in for supported files.

## LiteParse options

LiteParse is optional. Install it with:

```bash
pip install "make-markdown-library[liteparse]"
# or
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

| Policy | Behaviour |
| --- | --- |
| `include` | Include normal Markdown directly and import sections from existing generated libraries. Default. |
| `import-libs` | Import sections from generated Markdown libraries; skip ordinary Markdown files. |
| `skip` | Skip Markdown files entirely. |

Generated manifests, index files, and split Markdown outputs are skipped by default to avoid recursive self-ingestion. Use `--include-generated` only when you intentionally want those files included.

## Outputs

A successful build writes:

| Output | Purpose |
| --- | --- |
| `markdown-library.md` | Combined AI-readable Markdown library. |
| `markdown-library-manifest.md` | Human-readable table of every file found and what happened to it. |
| `markdown-library.index.json` | Machine-readable index, schema `1.1`. |
| `markdown-library.index.yaml` | Optional YAML index. |
| `markdown-library-files/` | Optional one Markdown file per included source. |

Example terminal output:

```text
Done. Markdown library created.
  Library:  /path/to/markdown-library.md
  Manifest: /path/to/markdown-library-manifest.md
  JSON index: /path/to/markdown-library.index.json
  Sources included: 12
  Sources skipped:  2
  Individual files: 12 in /path/to/markdown-library-files
```

## Index schema 1.1

Each source record includes:

- full SHA-256 and short fingerprint;
- converter, converter version, converter mode, and converter options;
- fallback metadata;
- output character, line, and word counts;
- PDF complexity metadata when checked;
- Markdown policy/generated/import metadata;
- source section line and character offsets when included.

## Python API

```python
from make_markdown_library import core

result = core.build_library(
    "sources",
    "markdown-library.md",
    individual_files=True,
    converter_mode="auto",
    markdown_policy="include",
    index_format="json",
    liteparse_options={
        "complexity_check": True,
        "image_mode": "placeholder",
        "ocr_language": "eng",
        "dpi": 150,
    },
)

print(result.converted_count, result.skipped_count)
print(result.index_path)
```

## Documentation

See `docs/`:

- `docs/getting-started.md`
- `docs/cli-reference.md`
- `docs/output-reference.md`
- `docs/guides/converter-modes.md`
- `docs/guides/ocr-and-pdfs.md`
- `docs/guides/indexes-json-yaml.md`
- `docs/troubleshooting.md`

## Develop

```bash
pip install -e ".[dev]"
pytest
```

Optional docs dependencies:

```bash
pip install -e ".[docs]"
```

## License

MIT.
