# Agent workflows

Make Markdown Library is useful for coding agents and LLM workflows because it creates one stable, source-delimited Markdown file plus a machine-readable index.

Recommended tiers:

1. Install Make Markdown Library normally.
2. Install LiteParse when PDF/OCR/layout support matters.
3. Use `llms.txt` and the `docs/` folder to help agents understand the repository.

Generate a machine-readable command summary with:

```bash
make-markdown-library make sources -o library.md --summary-json
```
