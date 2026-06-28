# make-markdown-library

Make Markdown Library turns messy folders, files, and ZIP archives into reproducible **AI-readable Markdown libraries** with manifests, JSON/YAML indexes, optional split Markdown files, and MarkItDown/LiteParse converter routing.

- **Documentation site:** https://markbeachill.github.io/make-markdown-library/
- **GitHub repository:** https://github.com/markbeachill/make-markdown-library
- **Download ZIP:** https://github.com/markbeachill/make-markdown-library/archive/refs/heads/main.zip

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

## What’s new in v3.4 / 0.3.4

- Public documentation pages now point to the real project links: GitHub repository, deployed site, and downloadable ZIP.
- The generated HTML site no longer includes self-referential build/deployment guide pages in the public navigation or broken per-page Markdown links.
- Site links are configured centrally in `site.config.json` and are set to the real GitHub repository and deployed GitHub Pages URL.
- GitHub Pages/build instructions remain in the repository README and source docs for maintainers.

v3.1 added the formal processing rules / safety contract and overwrite protections. v3.2 turned those docs into a real browsable site. v3.3 added the GitHub Pages workflow. v3.4 makes the published site read like end-user product docs.

## Quick start

```bash
pip install -e .
make-markdown-library make sources -o markdown-library.md --converter auto
```

If `markdown-library.md` already exists, choose a safety behaviour:

```bash
make-markdown-library make sources -o markdown-library.md --backup-existing
# or
make-markdown-library make sources -o markdown-library.md --overwrite
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

## Processing rules and overwrite safety

Version 3.1 defines an explicit behaviour contract. The short form:

- source defaults to `sources/`; output defaults to `markdown-library.md`;
- source and destination can be the same folder;
- a single source file cannot also be the output file;
- generated outputs are excluded from scanning by default;
- normal Markdown files are included directly;
- generated manifests, indexes, and split files are skipped by default;
- `make` refuses to overwrite existing main outputs unless `--overwrite` or `--backup-existing` is used;
- `add` and `rebuild` create backups by default;
- individual split outputs do not overwrite user-authored Markdown unless `--overwrite-individual` is used.

Read the full contract: `docs/processing-rules.md`.

Useful safety options:

```text
--backup-existing
--overwrite
--clean-individual-dir
--overwrite-individual
--allow-individual-in-source
```

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

The repository now includes both editable Markdown documentation and a generated multi-page HTML site.

```text
docs/                         Editable Markdown source
site/index.html                Browsable static HTML documentation
site/getting-started/          HTML page
site/processing-rules/         HTML page
site/guides/...                HTML guide pages
scripts/build_static_site.py   Rebuilds site/ from docs/
```

Open locally:

```text
site/index.html
```

Rebuild the static site after editing Markdown docs:

```bash
python scripts/build_static_site.py
```

### GitHub Pages deployment

The repository includes a ready-to-use GitHub Actions workflow for publishing the generated HTML site:

```text
.github/workflows/publish-site.yml
```

To enable it on GitHub, open **Settings → Pages** and set **Source** to **GitHub Actions**. The workflow rebuilds `site/` from `docs/` and deploys the generated HTML. See `docs/guides/github-pages.md` for the full setup.

MkDocs Material remains available as an optional alternative:

```bash
pip install -e ".[docs]"
mkdocs serve
```

Key docs:

- `docs/getting-started.md`
- `docs/cli-reference.md`
- `docs/output-reference.md`
- `docs/processing-rules.md`
- `docs/guides/converter-modes.md`
- `docs/guides/ocr-and-pdfs.md`
- `docs/guides/static-html-site.md`
- `docs/guides/github-pages.md`
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

## Maintaining the documentation site

The public documentation site is generated from the Markdown source docs. Maintainer notes live here rather than in the public site navigation.

```text
docs/                         Editable Markdown documentation source
site/                         Generated static HTML site for GitHub Pages
scripts/build_static_site.py   Dependency-free static site generator
.github/workflows/publish-site.yml  GitHub Pages deployment workflow
```

Project URLs are configured in `site.config.json`:

```json
{
  "site_url": "https://markbeachill.github.io/make-markdown-library/",
  "repo_url": "https://github.com/markbeachill/make-markdown-library",
  "download_url": "https://github.com/markbeachill/make-markdown-library/archive/refs/heads/main.zip",
  "issues_url": "https://github.com/markbeachill/make-markdown-library/issues"
}
```

To rebuild locally:

```bash
python scripts/build_static_site.py
```

To deploy, enable GitHub Pages with **Settings → Pages → Source → GitHub Actions**. The included workflow publishes the generated `site/` folder.

## License

MIT.
