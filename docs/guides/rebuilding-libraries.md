# Rebuilding libraries

Rebuilds use a previous JSON index to recreate a library more predictably than starting from scratch.

## Basic rebuild

```bash
make-markdown-library rebuild markdown-library.index.json
```

The tool reads the index, checks original source paths and hashes, and rebuilds outputs according to the recorded settings where possible.

## Dry run

Preview first:

```bash
make-markdown-library rebuild markdown-library.index.json --dry-run
```

Dry run reports what would be rebuilt, skipped, or missing without writing files.

## Backup behaviour

By default, rebuild backs up existing outputs before replacing them.

To replace without backups, be explicit:

```bash
make-markdown-library rebuild markdown-library.index.json --no-backup-existing --overwrite
```

## When to rebuild instead of add

Use `add` when you want to append new material.

Use `rebuild` when:

- source files changed;
- converter options changed;
- you want stale sections removed;
- you want a clean, reproducible library from the index.
