# Troubleshooting

## MarkItDown is missing

Run:

```bash
make-markdown-library setup markitdown
```

or install manually:

```bash
pip install markitdown
```

Then check:

```bash
make-markdown-library doctor
```

## LiteParse is missing

Run:

```bash
make-markdown-library setup liteparse
```

or install manually:

```bash
pip install liteparse
```

If using LiteParse multi-format conversion, check external tools such as LibreOffice and ImageMagick with `doctor`.

## YAML output fails

Install YAML support:

```bash
make-markdown-library setup yaml
```

or use JSON only:

```bash
--index-format json
```

## The tool skipped generated Markdown

This is intentional. Generated manifests, indexes, and split files are skipped by default to avoid recursive ingestion.

Use this only if recursive ingestion is intentional:

```bash
--include-generated
```

## A PDF converted to empty text

Use automatic fallback or LiteParse directly:

```bash
make-markdown-library make sources --converter auto
make-markdown-library make sources --converter liteparse
```

For scanned PDFs:

```bash
make-markdown-library make sources --converter auto --liteparse-complexity-check
```

## The tool refuses to overwrite outputs

This is a safety feature. Choose one:

```bash
--backup-existing
--overwrite
```

Prefer `--backup-existing` unless replacement without backup is intentional.

## Individual files collide with existing Markdown

By default, existing user-authored Markdown is protected and the tool writes a numbered filename.

To allow overwrite deliberately:

```bash
--overwrite-individual
```

## The individual output directory is the source folder

This is refused by default because generated Markdown could collide with real source Markdown.

Use a separate directory:

```bash
--individual-dir converted-md
```

or explicitly allow the risky setup:

```bash
--allow-individual-in-source
```
