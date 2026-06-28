# Install on Windows from the ZIP download

This guide assumes you are starting as a normal Windows user from the public documentation site.

## 1. Download the ZIP

Open the project download link:

- [Download the latest ZIP](https://github.com/markbeachill/make-markdown-library/archive/refs/heads/main.zip)

Your browser will usually save it to Downloads as:

```text
make-markdown-library-main.zip
```

## 2. Unzip it first

Before running any `pip install` command, extract the ZIP.

In File Explorer:

1. Open Downloads.
2. Right-click `make-markdown-library-main.zip`.
3. Choose **Extract All...**.
4. Accept the suggested folder or choose a folder you can find again.

After extraction, you should have a folder like:

```text
Downloads\make-markdown-library-main  README.md
  pyproject.toml
  make_markdown_library  docs  site```

The important thing is that `pyproject.toml` is visible in the folder. `pip install -e .` must be run from that extracted folder, not from inside the ZIP file.

## 3. Open PowerShell in the extracted folder

In File Explorer, open the extracted `make-markdown-library-main` folder.

Then do one of these:

- Click the address bar, type `powershell`, and press Enter.
- Or right-click inside the folder and choose **Open in Terminal**.

Check that you are in the right folder:

```powershell
Get-ChildItem
```

You should see `pyproject.toml` in the output.

## 4. Create a virtual environment

A virtual environment keeps the tool and its Python packages separate from the rest of your computer.

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation scripts, run this once in the same PowerShell window, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

When activation works, your prompt usually starts with:

```text
(.venv)
```

## 5. Install the tool

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install Make Markdown Library from the extracted folder:

```powershell
pip install -e .
```

That dot means “install the project in the current folder.” This is why you need to unzip first and run the command from the folder containing `pyproject.toml`.

## 6. Check it works

```powershell
make-markdown-library --version
make-markdown-library doctor
```

If the command is not found, keep the virtual environment activated and try:

```powershell
python -m make_markdown_library --version
```

## 7. Build your first library

Create a simple source folder:

```powershell
New-Item -ItemType Directory -Force sources
Set-Content sources
otes.md "# Notes`n`nThis is a test."
```

Build a Markdown library:

```powershell
make-markdown-library make sources -o markdown-library.md --converter auto
```

If `markdown-library.md` already exists, choose a safety option:

```powershell
make-markdown-library make sources -o markdown-library.md --backup-existing
```

or, when replacement is intentional:

```powershell
make-markdown-library make sources -o markdown-library.md --overwrite
```

## 8. Optional: install LiteParse support

LiteParse is optional. Install it only if you want the LiteParse converter/fallback features:

```powershell
pip install -e ".[liteparse]"
```

Then check again:

```powershell
make-markdown-library doctor
```

## 9. Optional: use the GUI

```powershell
python -m make_markdown_library gui
```

The GUI lets you choose the source folder, output file, converter mode, Markdown policy, and index format without typing the full command.

## Common Windows problems

### `py` is not recognized

Install Python from python.org or the Microsoft Store, then reopen PowerShell. During installation, enable the option to add Python to PATH if offered.

### `pip install -e .` says there is no `pyproject.toml`

You are in the wrong folder, or you are still inside the ZIP file. Extract the ZIP, open the extracted folder, and run:

```powershell
Get-ChildItem pyproject.toml
```

If that command does not find the file, move up or down folders until it does.

### PowerShell will not activate `.venv`

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This changes the policy only for the current PowerShell window.
