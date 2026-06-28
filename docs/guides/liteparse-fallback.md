# LiteParse fallback

LiteParse fallback exists because some documents technically convert but produce no useful text with a broad converter.

## Common fallback cases

- scanned PDF;
- image-only PDF;
- PDF with inaccessible text layer;
- Office document converted through a path that loses content;
- document where MarkItDown returns whitespace or an empty string.

## Use auto mode

```bash
make-markdown-library make sources -o library.md --converter auto
```

In this mode, the tool tries MarkItDown first for broad compatibility. If MarkItDown output is empty, LiteParse is attempted when available and supported for that file type.

## Use hybrid mode

```bash
make-markdown-library make sources -o library.md --converter hybrid
```

Hybrid mode prefers LiteParse for PDFs and layout-heavy documents while still using MarkItDown for formats where it is the broader, lighter default.

## Add complexity routing

```bash
make-markdown-library make sources -o library.md \
  --converter auto \
  --liteparse-complexity-check
```

This can prefer LiteParse before MarkItDown for complex PDFs.

## What gets recorded

The manifest and index record fallback decisions. Example:

```json
{
  "converter": "liteparse",
  "fallback": {
    "used": true,
    "from": "markitdown",
    "to": "liteparse",
    "reason": "markitdown_empty_output"
  }
}
```

Use `--verbose` to see fallback decisions in the terminal.
