# Agent workflows

Make Markdown Library is useful for coding agents and LLM workflows because it creates one stable, source-delimited Markdown file plus a machine-readable index.

## Why agents like it

Agents work better when context is:

- plain text;
- source-delimited;
- reproducible;
- small enough to inspect;
- backed by machine-readable metadata.

The combined library gives the text. The index gives provenance and rebuild metadata.

## Recommended tiers

1. Install Make Markdown Library normally.
2. Install LiteParse when PDF/OCR/layout support matters.
3. Use `llms.txt` and the `docs/` folder to help agents understand the repository.
4. Use `--summary-json` for machine-readable command output.

## Generate a library for an agent

```bash
make-markdown-library make project-docs -o agent-library.md \
  --converter auto \
  --index-format json \
  --summary-json
```

## Agent-readable documentation

The repository includes:

```text
llms.txt
```

It summarises purpose, commands, outputs, converter modes, processing rules, and docs locations.

## Raw Markdown and HTML docs

Documentation is maintained as Markdown in `docs/` and published as static HTML in `site/`. Agents can read either form.
