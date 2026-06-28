# Converter modes

Converter modes control how source files become Markdown.

## Modes

| Mode | Behaviour | Best for |
| --- | --- | --- |
| `markitdown` | Use MarkItDown only for supported non-Markdown files. | Broad Office/HTML/CSV conversion. |
| `liteparse` | Use LiteParse only where supported. | PDFs, OCR, images, and layout-sensitive documents. |
| `auto` | Direct-ingest Markdown/text, try MarkItDown first, and fall back to LiteParse if output is empty. With complexity checking, complex PDFs can prefer LiteParse first. | Safe mixed folders. |
| `hybrid` | Direct-ingest Markdown/text, prefer LiteParse for PDFs, and use MarkItDown for broad format coverage. | Layout-heavy projects. |

## Direct ingestion always comes first

These files are not sent through either converter:

```text
.md, .markdown, .txt, .csv, .json, .jsonl, .xml, .log
```

Markdown files are already Markdown. Text-like files can be wrapped directly with source metadata.

## Empty-output fallback

In `auto` and `hybrid`, MarkItDown may produce no readable text for some PDFs or image-heavy files. The tool checks:

```text
converted_text.strip() == ""
```

If the output is empty and LiteParse supports the file type, LiteParse is tried as a fallback. The index records:

```json
{
  "fallback": {
    "used": true,
    "from": "markitdown",
    "to": "liteparse",
    "reason": "markitdown_empty_output"
  }
}
```

## PDF complexity routing

Use:

```bash
--liteparse-complexity-check
```

When enabled, the tool may use LiteParse's complexity check for PDFs before conversion. Complex, scanned, or OCR-heavy PDFs can be routed to LiteParse first.

## Converter metadata

Every included source records:

```text
converter
converter_version
converter_mode
converter_options
fallback metadata
output statistics
```

This makes a library easier to audit and rebuild.
