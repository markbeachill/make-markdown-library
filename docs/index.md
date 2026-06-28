# What is Make Markdown Library?

Make Markdown Library turns messy folders, files, and ZIP archives into reproducible AI-readable Markdown libraries.

It is a local-first document ingestion tool. It gathers source material, preserves source boundaries, converts supported files to Markdown, writes a human-readable manifest, and records a machine-readable JSON or YAML index that can be used later for rebuilds, audits, search, and automation.

## Install and download

- [Download Make Markdown Library](download.md)
- [Install on Windows](guides/windows-install.md)
- [Install Python on Windows](guides/install-python-windows.md)
- [View the GitHub repository](https://github.com/markbeachill/make-markdown-library)
- [Open the published documentation site](https://markbeachill.github.io/make-markdown-library/)

The user-facing download is the Python wheel installer. The GitHub repository is for source code, issues, and developer work.

## What can it do?

- Build a combined Markdown library from a folder, file, or ZIP archive.
- Preserve one section per source, including the source path and fingerprint.
- Include normal Markdown files directly without re-converting them.
- Import existing generated Markdown libraries when requested by policy.
- Skip generated manifests, indexes, and split Markdown outputs by default.
- Use MarkItDown, LiteParse, auto routing, or hybrid routing.
- Fall back to LiteParse when MarkItDown returns empty output.
- Optionally route complex PDFs to LiteParse before conversion.
- Write one Markdown file per included source.
- Produce a JSON/YAML index with hashes, converter options, fallback metadata, output statistics, Markdown metadata, and section offsets.
- Refuse risky overwrite and recursive-output cases unless the user opts in.

## Core workflow

1. Install the tool once into Python.
2. Choose a folder, file, or ZIP archive to convert.
3. Choose where the library should be written.
4. Choose a converter mode.
5. Let the tool classify each file as source, Markdown, generated output, existing library, ZIP container, duplicate, or unsupported.
6. Convert, import, or directly ingest each source.
7. Write the combined Markdown library.
8. Write the manifest and index.
9. Optionally write individual Markdown files.
10. Use the processing contract to know exactly what was scanned, skipped, backed up, overwritten, or protected.

## Start here

- [Getting started](getting-started.md)
- [Download Make Markdown Library](download.md)
- [Install on Windows](guides/windows-install.md)
- [Processing rules and safety contract](processing-rules.md)
- [CLI reference](cli-reference.md)
- [Output reference](output-reference.md)
- [Converter modes](guides/converter-modes.md)
- [Markdown folders](guides/markdown-folders.md)
- [OCR, PDFs, and images](guides/ocr-and-pdfs.md)
- [Uninstall](guides/uninstall.md)

## Local-first by design

The tool reads local files and writes local outputs. Optional converters such as MarkItDown and LiteParse run locally when installed. LiteParse can also use local OCR tooling for scanned or image-heavy documents.

## Designed for AI workflows

A generated library is intentionally plain Markdown. It can be dropped into an LLM context, checked into Git, searched with ordinary tools, or fed into downstream RAG/indexing pipelines. The index keeps the Markdown output auditable and reproducible.
