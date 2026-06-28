# Output reference

A normal build writes these outputs.

| Output | Purpose |
| --- | --- |
| `markdown-library.md` | Combined AI-readable Markdown library. |
| `markdown-library-manifest.md` | Human-readable status table for all found files. |
| `markdown-library.index.json` | Machine-readable index, schema `1.1`. |
| `markdown-library.index.yaml` | Optional YAML index. |
| `markdown-library-files/` | Optional one Markdown file per included source. |

Example CLI output:

```text
Done. Markdown library created.
  Library:  /path/to/markdown-library.md
  Manifest: /path/to/markdown-library-manifest.md
  JSON index: /path/to/markdown-library.index.json
  Sources included: 12
  Sources skipped:  2
```

## Index schema 1.1

Each source entry records:

- `sha256` and `fingerprint`;
- `converter`, `converter_version`, `converter_mode`, and `converter_options`;
- `output.char_count`, `output.line_count`, and `output.word_count`;
- `fallback.used`, `fallback.from`, `fallback.to`, and `fallback.reason`;
- `complexity.checked`, `complexity.complex`, and `complexity.reason`;
- `markdown.policy`, `markdown.generated`, and `markdown.library_import`;
- `library_section` offsets when the source is included.
