# Troubleshooting

## MarkItDown is missing

Use the setup helper:

```bash
make-markdown-library setup markitdown
```

Or install MarkItDown manually:

```bash
pip install markitdown
```

Then check the environment:

```bash
make-markdown-library doctor
```

## LiteParse is missing

Use the setup helper:

```bash
make-markdown-library setup liteparse
```

Or install LiteParse manually:

```bash
pip install liteparse
```

If using LiteParse multi-format conversion, check external tools such as LibreOffice and ImageMagick with `doctor`. On Windows, use the [Windows prerequisites](guides/windows-prerequisites.md) guide for Tesseract OCR, LibreOffice, ImageMagick, and PATH checks.

## YAML output fails

Install YAML support:

```bash
make-markdown-library setup yaml
```

Or use JSON only:

```bash
make-markdown-library make sources --index-format json
```

## The tool skipped generated Markdown

This is intentional. Generated manifests, indexes, and split files are skipped by default to avoid recursive ingestion.

Use this only if recursive ingestion is intentional:

```bash
make-markdown-library make sources --include-generated
```

## A PDF converted to empty text

Use automatic fallback:

```bash
make-markdown-library make sources --converter auto
```

Or use LiteParse directly:

```bash
make-markdown-library make sources --converter liteparse
```

For scanned PDFs, add the LiteParse complexity check:

```bash
make-markdown-library make sources --converter auto --liteparse-complexity-check
```

## The tool refuses to overwrite outputs

This is a safety feature.

Choose backup mode if you want to keep the previous output:

```bash
make-markdown-library make sources -o markdown-library.md --backup-existing
```

Choose overwrite mode only when replacement is intentional:

```bash
make-markdown-library make sources -o markdown-library.md --overwrite
```

Prefer `--backup-existing` unless replacement without backup is intentional.

## Individual files collide with existing Markdown

By default, existing user-authored Markdown is protected and the tool writes a numbered filename.

To allow overwrite deliberately:

```bash
make-markdown-library make sources -o markdown-library.md --individual-files --overwrite-individual
```

## The individual output directory is the source folder

This is refused by default because generated Markdown could collide with real source Markdown.

Use a separate directory:

```bash
make-markdown-library make sources -o markdown-library.md --individual-files --individual-dir converted-md
```

Or explicitly allow the risky setup:

```bash
make-markdown-library make sources -o sources/markdown-library.md --individual-files --individual-dir sources --allow-individual-in-source
```
