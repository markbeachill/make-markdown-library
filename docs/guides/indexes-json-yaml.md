# JSON and YAML indexes

The index is the machine-readable audit trail for a build.

## Default format

JSON is written by default:

```bash
make-markdown-library make sources -o library.md
```

Output:

```text
library.index.json
```

## YAML and both formats

Write only a YAML index:

```bash
make-markdown-library make sources -o library.md --index-format yaml
```

Write both JSON and YAML indexes:

```bash
make-markdown-library make sources -o library.md --index-format both
```

YAML requires PyYAML:

```bash
pip install "make-markdown-library[yaml]"
```

## Why the index exists

The Markdown library is for reading. Its front matter contains a compact viewer index. The external JSON/YAML index is for tools.

It supports:

- rebuilds;
- duplicate detection;
- source provenance;
- converter audits;
- fallback audits;
- output statistics;
- future RAG/search workflows.

## Schema 1.2 source entry

A source record can contain:

```json
{
  "id": "src_abc123def456",
  "status": "included",
  "relative_path": "reports/report.pdf",
  "sha256": "...",
  "fingerprint": "9963f8ff36b0",
  "converter": "liteparse",
  "converter_mode": "auto",
  "converter_options": {
    "image_mode": "placeholder",
    "ocr_language": "eng"
  },
  "fallback": {
    "used": true,
    "from": "markitdown",
    "to": "liteparse",
    "reason": "markitdown_empty_output"
  },
  "output": {
    "char_count": 12345,
    "line_count": 320,
    "word_count": 2100
  }
}
```

## Custom index path

```bash
make-markdown-library make sources -o library.md --index-path metadata/library-index.json
```

If you customise output paths, keep the index with the generated library so rebuilds remain obvious.
