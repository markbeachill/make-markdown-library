# Getting started

This page walks through download, installation, your first successful build, and the safety choices you should understand before using the tool on a real project folder.

## Download

Download the latest repository ZIP:

- [Download ZIP](https://github.com/markbeachill/make-markdown-library/archive/refs/heads/main.zip)
- [View on GitHub](https://github.com/markbeachill/make-markdown-library)

After downloading, unzip the file first. You cannot run the install command from inside the ZIP archive.

## Windows install, step by step

1. Open Downloads.
2. Right-click `make-markdown-library-main.zip`.
3. Choose **Extract All...**.
4. Open the extracted `make-markdown-library-main` folder.
5. Check that the folder contains `pyproject.toml`.
6. Click the File Explorer address bar, type `powershell`, and press Enter.

In PowerShell, run the following commands one at a time.

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked, run this command:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run the activation command again:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the project:

```powershell
pip install -e .
```

Check the installed command:

```powershell
make-markdown-library --version
```

Run diagnostics:

```powershell
make-markdown-library doctor
```

For a fuller Windows walkthrough, see [Install on Windows](guides/windows-install.md).

## macOS or Linux install

Unzip the download, open a terminal in the extracted folder, then run these commands one at a time.

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project:

```bash
pip install -e .
```

Check the installed command:

```bash
make-markdown-library --version
```

Run diagnostics:

```bash
make-markdown-library doctor
```

## Optional converter extras

LiteParse and YAML output are optional extras. Use these commands from the extracted repository folder while your virtual environment is active.

Install LiteParse support:

```bash
pip install -e ".[liteparse]"
```

Install YAML output support:

```bash
pip install -e ".[yaml]"
```

Install all converter extras:

```bash
pip install -e ".[all-converters]"
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
make-markdown-library make sources -o markdown-library.md
```

The default `make` command refuses to overwrite existing outputs. If the outputs already exist, choose one explicit behaviour.

Keep a backup of the previous output:

```bash
make-markdown-library make sources -o markdown-library.md --backup-existing
```

Replace the previous output intentionally:

```bash
make-markdown-library make sources -o markdown-library.md --overwrite
```

Use `--backup-existing` when you care about preserving the previous library. Use `--overwrite` only when replacing output files is intentional.

## Build into a destination folder

If the second positional path is a folder, the library is written inside it:

```bash
make-markdown-library make sources out/
```

That creates:

```text
out/markdown-library.md
out/markdown-library-manifest.md
out/markdown-library.index.json
```

If the second positional path is a Markdown file, it is used as the exact output file:

```bash
make-markdown-library make sources out/research-pack.md
```

## Use automatic converter routing

Use `auto` mode:

```bash
make-markdown-library make sources -o markdown-library.md --converter auto
```

`auto` uses direct ingestion for Markdown/text-like inputs, tries MarkItDown for broad compatibility, and can fall back to LiteParse when MarkItDown returns empty output.

For scanned or layout-heavy PDFs, add the complexity check:

```bash
make-markdown-library make sources -o markdown-library.md --converter auto --liteparse-complexity-check
```

## Write individual Markdown files

```bash
make-markdown-library make sources -o markdown-library.md --individual-files
```

This writes one generated Markdown file per included source into:

```text
markdown-library-files/
```

Those generated files are outputs, not future source files. On later runs, the tool skips them by default to avoid recursive ingestion.

## Open the GUI

```bash
python -m make_markdown_library gui
```

The GUI exposes source/output selection, converter mode, Markdown policy, index format, LiteParse options, and output-folder opening.

## Read the contract before using source and output in the same folder

It is allowed to write outputs into the same folder you are scanning, but the exact skip and overwrite rules matter. Read [Processing rules](processing-rules.md) before doing this on an important folder.
