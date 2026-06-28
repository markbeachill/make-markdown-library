# OCR, PDFs, and images

PDFs and image-heavy documents are the hardest inputs to convert reliably. They may contain selectable text, scanned page images, embedded screenshots, charts, image-only tables, or mixed content.

## Basic PDF conversion

For simple born-digital PDFs:

```bash
make-markdown-library make sources -o library.md --converter auto
```

Auto mode tries MarkItDown first and can fall back to LiteParse if output is empty.

## Scanned or complex PDFs

For scanned, layout-heavy, or table-heavy PDFs:

```bash
make-markdown-library make sources -o library.md \
  --converter auto \
  --liteparse-complexity-check
```

This allows the tool to prefer LiteParse when a PDF looks complex or OCR-heavy.

## LiteParse options

```bash
make-markdown-library make sources -o library.md \
  --converter hybrid \
  --liteparse-image-mode placeholder \
  --liteparse-ocr-language eng \
  --liteparse-dpi 200
```

Supported option flags:

```text
--liteparse-image-mode off|placeholder|markdown|base64
--liteparse-no-links
--liteparse-no-ocr
--liteparse-ocr-language eng
--liteparse-target-pages 1,2,5-8
--liteparse-dpi 150
--liteparse-max-pages 50
--liteparse-password PASSWORD
--liteparse-complexity-check
```

## Images in PDFs and Office files

Image-containing files can mean different things:

| Image type | Desired behaviour |
| --- | --- |
| Logo/photo | Preserve a note or placeholder. |
| Image containing text | OCR the image where possible. |
| Diagram/chart/screenshot | Preserve visual context or at least record that image handling was needed. |
| Scanned page | Use OCR/layout-aware parsing. |

## What gets recorded

The index records converter options and complexity metadata so you can audit why a document used MarkItDown or LiteParse.

```json
{
  "complexity": {
    "checked": true,
    "complex": true,
    "reason": "ocr_required"
  },
  "converter_options": {
    "image_mode": "placeholder",
    "ocr_language": "eng",
    "dpi": 200
  }
}
```

## Practical recommendation

Use MarkItDown for structured Office/HTML/CSV material. Use LiteParse or hybrid routing for scanned PDFs, layout-sensitive PDFs, and image-heavy inputs where OCR or spatial layout matters.
