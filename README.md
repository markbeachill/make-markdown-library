# make-markdown-library

Turn a folder of mixed files — Word, PDF, PowerPoint, Markdown, HTML, CSV,
JSON, ZIPs, and more — into **one structured Markdown library file** an AI
chatbot can read. Optionally, also write **one Markdown file per source** and a
machine-readable **JSON/YAML index** for automation, audit trails, and rebuilds.

```
sources/                          markdown-library.md
  report.pdf          ─────►      (one readable file for AI)
  notes.docx                       markdown-library.index.json
  slides.pptx                     markdown-library-files/   (optional)
  existing-notes.md                  report.md
  extra.zip                         notes.md
                                    slides.md
```

## Why

- **AI** — paste one readable file into a chatbot instead of juggling attachments.
- **Storage** — keep a whole project's sources together in plain text.
- **Search** — find anything across every source at once.
- **Version control** — plain text diffs cleanly in Git; binaries don't.
- **Rebuilds** — the JSON index stores hashes, converter choices, and source sections.
- **Keeping** — Markdown stays readable for decades, with no special software.

## What's new in 0.2

- Converter strategy: `markitdown`, `liteparse`, `auto`, or `hybrid`.
- Optional LiteParse support for layout-aware local parsing.
- Existing Markdown files are read directly, not reconverted.
- Existing generated Markdown libraries can be imported as source sections.
- Generated manifests, indexes, and split Markdown files are skipped by default.
- JSON index output is written by default; YAML is optional.
- `doctor`, `setup`, and `rebuild` commands.

## Three ways to use it

### Use the window (simplest)

1. Install [Python](https://www.python.org/downloads/) (free, one time).
2. Download or clone this repository.
3. Run the GUI:

```bash
python -m make_markdown_library gui
```

A window opens: choose your folder, choose a converter strategy, tick "also make
one file per source" if you want it, press **Make library**. The GUI includes an
**Install LiteParse** button for users who want LiteParse-backed parsing.

### Use a terminal

```bash
# default: sources/ -> markdown-library.md + markdown-library.index.json
make-markdown-library make

# any folder, and also one file per source
make-markdown-library make my-folder -o library.md --individual-files

# use LiteParse for supported files
make-markdown-library make my-folder -o library.md --converter liteparse

# automatic routing: try MarkItDown first, then fall back to LiteParse when MarkItDown returns empty text
make-markdown-library make my-folder -o library.md --converter auto

# produce both JSON and YAML indexes
make-markdown-library make my-folder -o library.md --index-format both

# manage an existing library
make-markdown-library add library.md more.zip
make-markdown-library list library.md
make-markdown-library remove-file library.md 3
make-markdown-library check-file library.md

# check or install optional tools
make-markdown-library doctor
make-markdown-library setup liteparse
make-markdown-library setup all-converters

# rebuild from an index, reusing unchanged sections when possible
make-markdown-library rebuild markdown-library.index.json
```

### Build with it

```python
from make_markdown_library import core

result = core.build_library(
    "sources",
    "markdown-library.md",
    individual_files=True,
    converter_mode="auto",
    markdown_policy="include",
    index_format="json",
)

print(result.converted_count, result.skipped_count)
print(result.index_path)
for path in result.individual_files:
    print(path)
```

Every function returns plain data objects and never prints, so it's safe to use
as a library.

## What the tool outputs

A normal successful build prints a short terminal summary and writes files to
disk. For example:

```text
Done. Markdown library created.
  Library:  /path/to/markdown-library.md
  Manifest: /path/to/markdown-library-manifest.md
  JSON index: /path/to/markdown-library.index.json
  Sources included: 12
  Sources skipped:  2
  Individual files: 12 in /path/to/markdown-library-files
```

The files are:

| Output | Purpose |
| --- | --- |
| `markdown-library.md` | The combined AI-readable Markdown library. |
| `markdown-library-manifest.md` | Human-readable list of every file found and what happened to it. |
| `markdown-library.index.json` | Machine-readable index with hashes, converter choice, skipped reasons, and source offsets. |
| `markdown-library.index.yaml` | Optional YAML version when requested. |
| `markdown-library-files/` | Optional one-Markdown-file-per-source output. |

Skipped files and fallback events are visible in the manifest and index. For
example, if MarkItDown returns empty text and LiteParse succeeds, the source
record note says `converted after fallback: markitdown produced no readable text`.

## Converter choices

The default remains `markitdown` to preserve existing behaviour for broad file
coverage. You can opt into LiteParse or automatic routing:

| Mode | Behaviour |
| --- | --- |
| `markitdown` | Use MarkItDown for supported non-Markdown files. |
| `liteparse` | Use LiteParse for supported files; skip unsupported types. |
| `auto` | Try MarkItDown first for broad coverage; if it produces no readable text, try LiteParse for suffixes LiteParse supports. |
| `hybrid` | Alias for the same pragmatic mixed strategy as `auto`. |

Markdown and simple text formats are handled directly because they are already
text. This avoids unnecessary converter calls and preserves hand-written notes.

MarkItDown exposes converted Markdown text through its result object. The tool
therefore treats an empty or whitespace-only `text_content` value as “no readable
text found” and, in `auto`/`hybrid` mode, tries LiteParse before skipping the file.

## Installing LiteParse

LiteParse is optional. Install it through package extras or the built-in setup
command:

```bash
pip install "make-markdown-library[liteparse]"
# or
make-markdown-library setup liteparse
```

For a full conversion environment, use:

```bash
pip install "make-markdown-library[all-converters]"
# or
make-markdown-library setup all-converters
```

Run `make-markdown-library doctor` to check Python, MarkItDown, LiteParse, the
`lit` CLI, PyYAML, Tkinter, LibreOffice, and ImageMagick.

## When a folder already contains Markdown

Markdown files are first-class inputs.

| Policy | Behaviour |
| --- | --- |
| `include` | Include normal `.md` files directly and import sections from generated libraries. Default. |
| `import-libs` | Import sections from generated Markdown libraries; skip ordinary Markdown files. |
| `skip` | Skip Markdown files entirely. |

Generated manifests, index files, and split Markdown files are skipped by
default to prevent recursive libraries of libraries. Pass `--include-generated`
when you intentionally want those files included.

## Index files

By default, every build writes `markdown-library.index.json` next to the library.
The index records:

- source status, path, suffix, size, full SHA-256 hash, and short fingerprint;
- converter name and version;
- source kind, such as file, markdown, or imported library section;
- per-source Markdown path when split files are requested;
- library section line and character offsets; and
- skipped files and reasons.

Use `--index-format yaml` or `--index-format both` for YAML output. YAML requires
PyYAML, available through `pip install "make-markdown-library[yaml]"`.

## How the file is built

Each source becomes a clearly marked section, so an AI can always tell where one
source ends and the next begins. A short fingerprint spots duplicates; the JSON
index stores the full SHA-256 for exact matching.

```
<!-- markdown-library-file: true -->
======================================================================
SOURCE START
File: report.pdf
Fingerprint: 9963f8ff36b0
SHA256: 9963f8ff36b0...full hash...
Converter: liteparse 2.2.1
======================================================================

The converted text of your source, as plain Markdown.

======================================================================
SOURCE END: report.pdf
======================================================================
```

Duplicate sources are skipped by default; pass `--allow-duplicates` to keep them.

## Design

One engine, two faces. `core.py` does all the work and returns data. `cli.py`
(terminal) and `gui.py` (Tkinter window) are thin faces that call it. No
conversion logic lives in either face.

## Develop

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT.
