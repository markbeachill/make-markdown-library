# CLI reference

The command line interface is the most complete way to use Make Markdown Library.

## Command overview

```text
make-markdown-library make      Create a new library.
make-markdown-library add       Append new sources to an existing library.
make-markdown-library list      List source sections in a library.
make-markdown-library remove    Remove source sections by text match.
make-markdown-library check     Inspect a library and report source counts.
make-markdown-library rebuild   Rebuild from a JSON index.
make-markdown-library doctor    Check optional dependencies and tools.
make-markdown-library setup     Install optional dependency groups.
make-markdown-library gui       Open the graphical interface.
```

## `make`

Create a Markdown library from a folder, file, or ZIP archive.

```bash
make-markdown-library make [source] [destination] [options]
```

Defaults:

```text
source: sources/
output: markdown-library.md
```

Path examples:

Use the defaults, `sources/` and `markdown-library.md`:

```bash
make-markdown-library make
```

Set the source folder:

```bash
make-markdown-library make sources
```

Write into a destination folder:

```bash
make-markdown-library make sources out/
```

Write to an exact destination file:

```bash
make-markdown-library make sources out/library.md
```

Use the explicit output option:

```bash
make-markdown-library make sources -o out/library.md
```

Do not provide both a destination positional path and `--output`; the CLI rejects that.

### Make options

```text
-o, --output PATH                  Output library file.
-p, --purpose TEXT                 Purpose text written into the library header.
--description TEXT                 Library-level description written into front matter.
--category TEXT                    Library-level category written into front matter.
--allow-duplicates                 Include duplicate content instead of skipping it.
--individual-files                 Write one Markdown file per included source.
--individual-dir PATH              Directory for split Markdown outputs.
--converter MODE                   markitdown, liteparse, auto, or hybrid.
--md-policy POLICY                 include, import-libs, or skip.
--include-generated                Allow generated manifests, indexes, and split files as inputs.
--index-format FORMAT              json, yaml, both, or none.
--index-path PATH                  Custom JSON index path.
--verbose                          Print per-file routing and skip decisions.
--quiet                            Print only errors and essential final paths.
--summary-json                     Print a compact machine-readable build summary.
```

### Safety options

```text
--backup-existing                  Back up existing outputs before replacing them.
--overwrite                        Replace existing outputs without backups.
--clean-individual-dir             Remove old generated split Markdown files first.
--overwrite-individual             Allow split outputs to overwrite non-generated Markdown.
--allow-individual-in-source       Allow --individual-dir to be exactly the source folder.
```

By default, `make` refuses to overwrite existing library, manifest, and index outputs.

### LiteParse options

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

These options are recorded in the JSON/YAML index when LiteParse is used.

## `add`

Append sources to an existing library.

```bash
make-markdown-library add library.md new-files/
```

Default behaviour:

- reads existing source fingerprints from `library.md`;
- skips new sources with matching fingerprints;
- appends genuinely new sections;
- backs up the existing library before modifying it.

Options:

```text
--allow-duplicates
--converter markitdown|liteparse|auto|hybrid
--md-policy include|import-libs|skip
--no-backup-existing
```

`add` appends; it does not replace old sections by path. For replacement, remove first or rebuild from an index.

## `rebuild`

Rebuild from an existing JSON index.

```bash
make-markdown-library rebuild markdown-library.index.json
```

Preview without writing:

```bash
make-markdown-library rebuild markdown-library.index.json --dry-run
```

By default, rebuild backs up existing outputs before replacing them. Use `--no-backup-existing --overwrite` only when replacement without backup is intentional.

## `doctor`

Check the local environment:

```bash
make-markdown-library doctor
```

It reports Python version, MarkItDown availability, LiteParse Python package availability, the optional `lit` CLI, YAML support, GUI/Tkinter availability, LibreOffice, ImageMagick, and OCR-related tooling where detectable. On Windows, ImageMagick is detected with `magick`, not Windows `convert.exe`.

## `setup`

Install LiteParse support:

```bash
make-markdown-library setup liteparse
```

Install YAML support:

```bash
make-markdown-library setup yaml
```

Install all converter extras:

```bash
make-markdown-library setup all-converters
```

You normally choose the one dependency group you need. Interactive setup explains what will be installed before running pip. Non-interactive use should pass the tool's confirmation option where available.
