# Make Markdown Library Viewer

This is a first-pass static viewer for Markdown files and generated Make Markdown Library files.

Open `viewer/index.html` in a browser, then choose a `.md` file.

## What it does

- Opens ordinary Markdown files and renders them as formatted documents.
- Detects Make Markdown Library front matter.
- Builds a left-hand source list from the embedded library metadata.
- Uses `mmlib:source-start` / `mmlib:source-end` markers to show one source section at a time.
- Supports search/filter in the source list.
- Provides a raw/formatted toggle and copy-section button.

## Dependencies

The viewer is currently dependency-light and can run offline from the files in this folder.

If `markdown-it` and `DOMPurify` are loaded by a future wrapper or bundled build, the viewer will use them automatically. Otherwise, it uses a small built-in fallback renderer.

## Current limitations

- It is read-only.
- It opens one Markdown file at a time.
- The fallback Markdown renderer is intentionally simple; full CommonMark rendering should be added by bundling `markdown-it` locally in a later viewer build.
- It does not need `markdown-library.index.json` for basic navigation; it reads embedded front matter and section markers from the `.md` file.
