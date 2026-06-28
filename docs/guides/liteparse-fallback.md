# LiteParse fallback

In `auto` and `hybrid` modes, Make Markdown Library can try another converter when the first converter produces no readable text.

The common case is a PDF where MarkItDown returns empty or whitespace-only output. The tool records this as fallback metadata:

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
