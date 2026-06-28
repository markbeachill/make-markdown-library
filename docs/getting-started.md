# Getting started

This page walks through download, installation, your first successful build, and the safety choices you should understand before using the tool on a real project folder.

The most important idea is:

> Install Make Markdown Library once, then point it at any folder of documents.

You do **not** need to copy the tool into each project folder. You do **not** need to reinstall it for every new folder you want to convert.

## Download

Download the latest repository ZIP:

- [Download ZIP](https://github.com/markbeachill/make-markdown-library/archive/refs/heads/main.zip)
- [View on GitHub](https://github.com/markbeachill/make-markdown-library)

After downloading, unzip the file first. You cannot run the install command from inside the ZIP archive.

## Windows install

1. Find the downloaded `make-markdown-library-main.zip` file. It is often in Downloads.
2. Right-click `make-markdown-library-main.zip`.
3. Choose **Extract All...**.
4. Open the extracted `make-markdown-library-main` folder.
5. Check that the folder contains `pyproject.toml`.
6. Click the File Explorer address bar, type `powershell`, and press Enter.

Install the tool:

```powershell
py -m pip install .
```

Check it works:

```powershell
py -m make_markdown_library --version
```

Run diagnostics:

```powershell
py -m make_markdown_library doctor
```

You can now use the tool on any folder by passing the folder path to the command.

For a fuller Windows walkthrough, see [Install on Windows](guides/windows-install.md).

## macOS or Linux install

Unzip the download, open a terminal in the extracted folder, then install the tool:

```bash
python3 -m pip install .
```

Check it works:

```bash
python3 -m make_markdown_library --version
```

Run diagnostics:

```bash
python3 -m make_markdown_library doctor
```

If the short command is available on your PATH, you can use this instead:

```bash
make-markdown-library --version
```

## Optional converter extras

LiteParse and YAML output are optional extras. Use these commands from the extracted repository folder.

Install LiteParse support:

```bash
python -m pip install ".[liteparse]"
```

Install YAML output support:

```bash
python -m pip install ".[yaml]"
```

Install all converter extras:

```bash
python -m pip install ".[all-converters]"
```

You normally choose one of those commands, not all three.

## First build

Create a folder named `sources`, then put documents in it. For example:

```text
sources/
  report.pdf
  notes.md
  data.csv
```

Build the library:

```bash
python -m make_markdown_library make sources -o markdown-library.md
```

On Windows, use `py` if that is your Python launcher:

```powershell
py -m make_markdown_library make sources -o markdown-library.md
```

The default `make` command refuses to overwrite existing outputs. If the outputs already exist, choose one explicit behaviour.

Keep a backup of the previous output:

```bash
python -m make_markdown_library make sources -o markdown-library.md --backup-existing
```

Replace the previous output intentionally:

```bash
python -m make_markdown_library make sources -o markdown-library.md --overwrite
```

Use `--backup-existing` when you care about preserving the previous library. Use `--overwrite` only when replacing output files is intentional.

## Build into a destination folder

If the second positional path is a folder, the library is written inside it:

```bash
python -m make_markdown_library make sources out/
```

That creates:

```text
out/markdown-library.md
out/markdown-library-manifest.md
out/markdown-library.index.json
```

If the second positional path is a Markdown file, it is used as the exact output file:

```bash
python -m make_markdown_library make sources out/research-pack.md
```

## Use automatic converter routing

Use `auto` mode:

```bash
python -m make_markdown_library make sources -o markdown-library.md --converter auto
```

`auto` uses direct ingestion for Markdown/text-like inputs, tries MarkItDown for broad compatibility, and can fall back to LiteParse when MarkItDown returns empty output.

For scanned or layout-heavy PDFs, add the complexity check:

```bash
python -m make_markdown_library make sources -o markdown-library.md --converter auto --liteparse-complexity-check
```

## Write individual Markdown files

```bash
python -m make_markdown_library make sources -o markdown-library.md --individual-files
```

This writes one generated Markdown file per included source into:

```text
markdown-library-files/
```
