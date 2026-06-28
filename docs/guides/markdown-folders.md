# Folders that already contain Markdown

Normal `.md` files are added directly. They are already Markdown and do not need conversion.

Policies:

```text
--md-policy include       Include normal Markdown and import generated libraries. Default.
--md-policy import-libs   Import generated libraries; skip normal Markdown.
--md-policy skip          Skip Markdown files entirely.
```

Generated manifests, indexes, and split source files are skipped by default. Use `--include-generated` only when you want recursive ingestion.
