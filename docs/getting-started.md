# Getting started

This page walks through the first successful build and the safety choices you should understand before using the tool on a real project folder.

## Install

During development, install the package in editable mode:

```bash
pip install -e .
```

Optional converter extras:

```bash
pip install "make-markdown-library[liteparse]"
pip install "make-markdown-library[yaml]"
pip install "make-markdown-library[all-converters]"
```

Check the environment:

```bash
make-markdown-library doctor
```

## First build

Create a source folder:

```text
sources/
  report.pdf
  notes.md
  data.csv
```

Run:

```bash
make-markdown-library make sources -o markdown-library.md
```

The default `make` command refuses to overwrite existing outputs. If the outputs already exist, choose one explicit behaviour:

```bash
make-markdown-library make sources -o markdown-library.md --backup-existing
make-markdown-library make sources -o markdown-library.md --overwrite
```

Use `--backup-existing` when you care about preserving the previous library. Use `--overwrite` only when replacing output files is intentional.

## Build into a destination folder

If the second positional path is a folder, the library is written inside it:

```bash
make-markdown-library make sources out/
```

Output:

```text
out/markdown-library.md
out/markdown-library-manifest.md
out/markdown-library.index.json
```

If the second positional path is a Markdown file, it is used as the exact output file:

```bash
make-markdown-library make sources out/research-pack.md
```

## Use automatic converter routing

```bash
make-markdown-library make sources -o markdown-library.md --converter auto
```

`auto` uses direct ingestion for Markdown/text-like inputs, tries MarkItDown for broad compatibility, and can fall back to LiteParse when MarkItDown returns empty output.

For scanned or layout-heavy PDFs:

```bash
make-markdown-library make sources -o markdown-library.md \
  --converter auto \
  --liteparse-complexity-check
```

## Write individual Markdown files

```bash
make-markdown-library make sources -o markdown-library.md --individual-files
```

This writes one generated Markdown file per included source into:

```text
markdown-library-files/
```

Those generated files are outputs, not future source files. On later runs, the tool skips them by default to avoid recursive ingestion.

## Open the GUI

```bash
python -m make_markdown_library gui
```

The GUI exposes source/output selection, converter mode, Markdown policy, index format, LiteParse options, and output-folder opening.

## Read the contract before using source and output in the same folder

It is allowed to write outputs into the same folder you are scanning, but the exact skip and overwrite rules matter. Read [Processing rules](processing-rules.md) before doing this on an important folder.
