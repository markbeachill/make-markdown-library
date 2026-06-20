# make-markdown-library

Turn a folder of mixed files — Word, PDF, PowerPoint, Markdown, HTML, CSV, and
ZIPs — into **one structured Markdown file** an AI chatbot can read. Optionally,
also write **one Markdown file per source**.

```
sources/                          markdown-library.md
  report.pdf          ─────►      (one readable file for AI)
  notes.docx
  slides.pptx                     markdown-library-files/   (optional)
  extra.zip                         report.md
                                    notes.md
                                    slides.md
```

## Why

- **AI** — paste one readable file into a chatbot instead of juggling attachments.
- **Storage** — keep a whole project's sources together in plain text.
- **Search** — find anything across every source at once.
- **Version control** — plain text diffs cleanly in Git; binaries don't.
- **Keeping** — Markdown stays readable for decades, with no special software.

## Three ways to use it

### Use the window (simplest)

1. Install [Python](https://www.python.org/downloads/) (free, one time).
2. Download **`make-markdown-library.py`**.
3. Double-click it, or run `python make-markdown-library.py`.

A window opens: choose your folder, tick "also make one file per source" if you
want it, press **Make library**. The first run installs MarkItDown for you
(needs internet once); after that it works offline.

### Use a terminal

Same one file, driven by commands:

```bash
# default: sources/ -> markdown-library.md
python make-markdown-library.py make

# any folder, and also one file per source
python make-markdown-library.py make my-folder -o library.md --individual-files

# manage an existing library
python make-markdown-library.py add library.md more.zip
python make-markdown-library.py list library.md
python make-markdown-library.py remove-file library.md 3
python make-markdown-library.py check-file library.md
```

### Build with it

```python
from make_markdown_library import core

result = core.build_library("sources", "markdown-library.md", individual_files=True)
print(result.converted_count, result.skipped_count)
for path in result.individual_files:
    print(path)
```

Every function returns plain data objects and never prints, so it's safe to use
as a library.

## How the file is built

Each source becomes a clearly marked section, so an AI can always tell where one
source ends and the next begins. A short fingerprint spots duplicates and traces
each source back.

```
<!-- markdown-library-file: true -->
======================================================================
SOURCE START
File: report.pdf
Fingerprint: 9963f8ff36b0
======================================================================

The converted text of your source, as plain Markdown.

======================================================================
SOURCE END: report.pdf
======================================================================
```

Duplicate sources are skipped by default; pass `--allow-duplicates` to keep them.
Conversion uses [MarkItDown](https://github.com/microsoft/markitdown).

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
