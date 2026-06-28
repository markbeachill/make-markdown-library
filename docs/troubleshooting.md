# Troubleshooting

## MarkItDown is missing

```bash
make-markdown-library setup markitdown
```

## LiteParse is missing

```bash
make-markdown-library setup liteparse
```

## YAML output fails

```bash
make-markdown-library setup yaml
```

or use:

```bash
--index-format json
```

## The tool skipped generated Markdown

This is intentional. Generated manifests, indexes, and split files are skipped by default to avoid recursive ingestion. Use `--include-generated` to include them.

## A PDF converted to empty text

Use automatic fallback or LiteParse directly:

```bash
make-markdown-library make sources --converter auto
make-markdown-library make sources --converter liteparse
```
