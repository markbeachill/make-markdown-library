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

### Click to use

Download the app from the [releases page](https://github.com/beachill/make-markdown-library/releases),
open it, choose your folder, press **Make library**. If you already have Python,
`make-markdown-library gui` opens the same window.

### Use a terminal

```bash
pip install make-markdown-library

# default: sources/ -> markdown-library.md
make-markdown-library make

# any folder, and also one file per source
make-markdown-library make my-folder -o library.md --individual-files

# manage an existing library
make-markdown-library add library.md more.zip
make-markdown-library list library.md
make-markdown-library remove-file library.md 3
make-markdown-library check-file library.md
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
