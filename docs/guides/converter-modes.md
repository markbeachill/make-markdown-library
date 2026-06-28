# Converter modes

| Mode | Behaviour |
| --- | --- |
| `markitdown` | Use MarkItDown only. |
| `liteparse` | Use LiteParse only where supported. |
| `auto` | Use direct Markdown/text ingestion, try MarkItDown first, and fallback to LiteParse if output is empty. With complexity checking enabled, complex PDFs can prefer LiteParse first. |
| `hybrid` | Use direct Markdown/text ingestion, prefer LiteParse for PDFs, and use MarkItDown for broad format coverage. |

Use `--verbose` to see per-file routing decisions.
