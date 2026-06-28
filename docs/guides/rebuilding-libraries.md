# Rebuilding libraries

Rebuild from a JSON index:

```bash
make-markdown-library rebuild markdown-library.index.json
```

Preview first:

```bash
make-markdown-library rebuild markdown-library.index.json --dry-run
```

Dry-run output reports files that would rebuild, skip, or be removed because the original source is missing.
