# OCR and PDFs

LiteParse is useful for layout-heavy, scanned, or image-heavy PDFs.

Use complexity routing:

```bash
make-markdown-library make sources -o library.md \
  --converter auto \
  --liteparse-complexity-check
```

Tune LiteParse:

```bash
make-markdown-library make sources -o library.md \
  --converter hybrid \
  --liteparse-image-mode placeholder \
  --liteparse-ocr-language eng \
  --liteparse-dpi 200
```
