# Output reference

A normal build produces a combined Markdown library plus companion audit files.

## Default outputs

For an output library called:

```text
markdown-library.md
```

the companion files are:

| Output | When written | Purpose |
| --- | --- | --- |
| `markdown-library.md` | Always | Combined AI-readable Markdown library. |
| `markdown-library-manifest.md` | Always | Human-readable status table for found files. |
| `markdown-library.index.json` | Default | Machine-readable index, schema `1.1`. |
| `markdown-library.index.yaml` | With `--index-format yaml` or `both` | Optional YAML version of the index. |
| `markdown-library-files/` | With `--individual-files` | One generated Markdown file per included source. |

Example CLI output:

```text
Done. Markdown library created.
  Library:  /path/to/markdown-library.md
  Manifest: /path/to/markdown-library-manifest.md
  JSON index: /path/to/markdown-library.index.json
  Sources included: 12
  Sources skipped:  2
  Individual files: 12 in /path/to/markdown-library-files
```

## Combined library

The combined library is deliberately plain Markdown. Each included source is separated by source markers so humans and tools can identify boundaries.

A typical section contains:

```text
source path
source fingerprint
converter used
converter mode
fallback note, if any
converted or direct-ingested Markdown content
```

## Manifest

The manifest is for people. It records which files were included, imported, skipped, duplicated, unsupported, or failed.

Use it to answer:

- Did this file get included?
- Why was that file skipped?
- Which converter was used?
- Did fallback happen?
- Were duplicates detected?

## JSON/YAML index

The index is for automation. Schema `1.1` records:

```text
schema_version
tool name/version
library output path
source input path
build settings
included sources
skipped sources
```

Each source entry records:

- `sha256` and short `fingerprint`;
- source path, suffix, size, and parent archive if applicable;
- `converter`, `converter_version`, `converter_mode`, and `converter_options`;
- `output.char_count`, `output.line_count`, and `output.word_count`;
- `fallback.used`, `fallback.from`, `fallback.to`, and `fallback.reason`;
- `complexity.checked`, `complexity.complex`, and `complexity.reason`;
- `markdown.policy`, `markdown.generated`, and `markdown.library_import`;
- `library_section` offsets when the source is included;
- individual Markdown output path when split files are enabled.

## Individual files

With:

```text
--individual-files
```

the tool writes split outputs to the default directory:

```text
markdown-library-files/
```

Each split file starts with a source marker. Generated split files are skipped on future runs by default.

## Overwrite and backup behaviour

`make` refuses to replace existing library, manifest, and index outputs unless you choose one of these options:

- `--backup-existing` keeps backup copies before replacing outputs.
- `--overwrite` replaces outputs without backups.

`--backup-existing` writes backups such as:

```text
markdown-library.backup.md
markdown-library-manifest.backup.md
markdown-library.index.backup.json
```

`add`, `rebuild`, and `remove-file` back up existing libraries before modifying them by default.

## Individual output collisions

Existing user-authored Markdown is protected. If a generated split file would collide with an existing non-generated Markdown file, the tool chooses a numbered filename unless `--overwrite-individual` is set.

```text
project.md      # user-authored, preserved
project-2.md    # generated output
```
