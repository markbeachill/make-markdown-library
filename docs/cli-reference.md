# CLI reference

## `make`

Create a Markdown library from a folder, file, or ZIP.

```bash
make-markdown-library make [source] [destination] [options]
```

Common options:

```text
-o, --output PATH
-p, --purpose TEXT
--allow-duplicates
--individual-files
--individual-dir PATH
--converter markitdown|liteparse|auto|hybrid
--md-policy include|import-libs|skip
--include-generated
--index-format json|yaml|both|none
--index-path PATH
--verbose
--quiet
--summary-json
```

LiteParse options:

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

## `rebuild`

Rebuild from an existing JSON index.

```bash
make-markdown-library rebuild markdown-library.index.json
make-markdown-library rebuild markdown-library.index.json --dry-run
```

## `add`

Add new sources to an existing library.

```bash
make-markdown-library add library.md new-sources/
```

## `list`

```bash
make-markdown-library list library.md
```

## `remove-file`

```bash
make-markdown-library remove-file library.md 3
make-markdown-library remove-file library.md report.pdf
```

## `check-file`

```bash
make-markdown-library check-file library.md
```

## `doctor`

```bash
make-markdown-library doctor
```

## `setup`

```bash
make-markdown-library setup liteparse
make-markdown-library setup all-converters --yes
```
