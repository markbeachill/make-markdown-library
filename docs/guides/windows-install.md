# Install on Windows from the ZIP download

This guide assumes you are starting from the public documentation site and have not used the project before.

The short version is: **download the ZIP, unzip it, open PowerShell in the extracted folder, then install from that folder.**

## 1. Download the ZIP

Open the project download link:

- [Download the latest ZIP](https://github.com/markbeachill/make-markdown-library/archive/refs/heads/main.zip)

Your browser will usually save a file called `make-markdown-library-main.zip` in your Downloads folder.

## 2. Unzip it first

Before running any `pip install` command, extract the ZIP.

In File Explorer:

1. Open Downloads.
2. Right-click `make-markdown-library-main.zip`.
3. Choose **Extract All...**.
4. Accept the suggested folder or choose a folder you can find again.

After extraction, open the new folder. It should contain files and folders like these:

```text
README.md
pyproject.toml
make_markdown_library/
docs/
site/
```

The important file is `pyproject.toml`. The install command must be run from the folder that contains that file.

## 3. Open PowerShell in the extracted folder

In File Explorer, open the extracted `make-markdown-library-main` folder.

Then choose one of these methods:

- Click the File Explorer address bar, type `powershell`, and press Enter.
- Or right-click inside the folder and choose **Open in Terminal**.

Run this command to check you are in the right place:

```powershell
Get-ChildItem pyproject.toml
```

If PowerShell lists `pyproject.toml`, continue.

If it says the file cannot be found, you are in the wrong folder. Move into the extracted `make-markdown-library-main` folder and try again.

## 4. Create a virtual environment

A virtual environment keeps this tool and its Python packages separate from the rest of your computer.

Run this command:

```powershell
py -m venv .venv
```

Then activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

When activation works, your prompt usually starts with `(.venv)`.

### If PowerShell blocks activation

If PowerShell says scripts are disabled, run this command in the same PowerShell window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run the activation command again:

```powershell
.\.venv\Scripts\Activate.ps1
```

This changes the policy only for the current PowerShell window.

## 5. Install the tool

First, upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Then install Make Markdown Library from the extracted folder:

```powershell
pip install -e .
```

The dot means “install the project in the current folder.” This is why you need to unzip first and run the command from the folder containing `pyproject.toml`.

## 6. Check it works

Check the installed command:

```powershell
make-markdown-library --version
```

Then run the diagnostic command:

```powershell
make-markdown-library doctor
```

If `make-markdown-library` is not found, keep the virtual environment activated and try the module form:

```powershell
python -m make_markdown_library --version
```

## 7. Build your first library

Create a simple source folder:

```powershell
New-Item -ItemType Directory -Force sources
```

Create a small Markdown note inside it:

```powershell
Set-Content .\sources\notes.md "# Notes`n`nThis is a test."
```

Build a Markdown library:

```powershell
make-markdown-library make sources -o markdown-library.md --converter auto
```

If `markdown-library.md` already exists, choose one of the safety options below.

To keep a backup of the existing output, run:

```powershell
make-markdown-library make sources -o markdown-library.md --backup-existing
```

To replace the existing output intentionally, run:

```powershell
make-markdown-library make sources -o markdown-library.md --overwrite
```

## 8. Optional: install LiteParse support

LiteParse is optional. Install it only if you want the LiteParse converter/fallback features.

Run this command while the virtual environment is active and PowerShell is still in the extracted project folder:

```powershell
pip install -e ".[liteparse]"
```

Then run the diagnostic command again:

```powershell
make-markdown-library doctor
```

## 9. Optional: use the GUI

Start the GUI with:

```powershell
python -m make_markdown_library gui
```

The GUI lets you choose the source folder, output file, converter mode, Markdown policy, and index format without typing the full `make` command.

## Common Windows problems

### `py` is not recognized

Install Python from python.org or the Microsoft Store, then reopen PowerShell. During installation, enable the option to add Python to PATH if offered.

### `pip install -e .` says there is no `pyproject.toml`

You are in the wrong folder, or you are still looking inside the ZIP file. Extract the ZIP, open the extracted folder, and run:

```powershell
Get-ChildItem pyproject.toml
```

If that command does not find the file, move up or down folders until it does.

### PowerShell will not activate `.venv`

Run this command:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

This changes the policy only for the current PowerShell window.
