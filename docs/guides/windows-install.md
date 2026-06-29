# Install on Windows

This page is for installing the tool, not for downloading the source repository.

The important idea is:

> Install Make Markdown Library once into Python, then run it against any folder of documents.

You do **not** install it into each document folder. You do **not** need to keep a copy of the GitHub source repository on your computer just to use the tool.

## 1. Check Python first

Open PowerShell and run:

```powershell
py --version
```

If that prints a Python version, continue.

If it does not work, install Python first:

- [Install Python on Windows](install-python-windows.md)

## 2. Download the install package

Use the public download page:

- [Download Make Markdown Library](../download.md)

The primary button on that page downloads the `.whl` installer directly. The same page also links to the GitHub release page as a fallback.

The install package is a Python wheel file. It has a name like:

```text
make_markdown_library-0.4.0-py3-none-any.whl
```

It is fine if the browser saves this file in Downloads. Downloads is only a temporary place for the installer file. It is **not** where the tool is installed.

## 3. Install the package

In PowerShell, install the downloaded wheel file.

If it is in your Downloads folder, run:

```powershell
py -m pip install --user "$env:USERPROFILE\Downloads\make_markdown_library-0.4.0-py3-none-any.whl"
```

The `--user` option installs the tool into your Windows user Python location. It avoids needing administrator permissions.

## 4. Where is it installed?

You normally do not choose an application folder.

Python installs the tool into your user Python package area, usually somewhere under your Windows profile, such as:

```text
C:\Users\YourName\AppData\Roaming\Python\Python3xx\site-packages
```

The command-line launcher may be placed under a matching `Scripts` folder.

That location is managed by Python and pip. You do not need to browse to it. You do not need to keep the wheel file after installation.

## 5. Check it works

Use the Python module form. This avoids Windows PATH problems:

```powershell
py -m make_markdown_library --version
```

Then run the diagnostic command:

```powershell
py -m make_markdown_library doctor
```

## 6. Use it on any folder

You can now run the tool from any PowerShell window by giving it the path to the folder you want to convert.

For example:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" --converter auto
```

That creates the default outputs in the current PowerShell folder.

To write the library into the document folder, use an output path:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" -o "C:\Users\Mark\Documents\My Project\markdown-library.md" --converter auto
```

If a library already exists, choose a safety behaviour.

Keep a backup of the previous output:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" -o "C:\Users\Mark\Documents\My Project\markdown-library.md" --backup-existing
```

Replace the previous output intentionally:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" -o "C:\Users\Mark\Documents\My Project\markdown-library.md" --overwrite
```

## 7. Optional: use the short command

Some Python installs make this shorter command available:

```powershell
make-markdown-library --version
```

If it works, you can use `make-markdown-library` instead of `py -m make_markdown_library`.

If it does not work, keep using the module form. It is longer, but reliable:

```powershell
py -m make_markdown_library --version
```

## 8. Optional: install Windows prerequisites

The tool can run without every optional system tool. If `doctor` reports missing OCR, LibreOffice, ImageMagick, or the `lit` CLI, use the prerequisites guide to decide what you actually need:

- [Windows prerequisites](windows-prerequisites.md)

For most users, the most useful optional extra is Tesseract OCR for scanned PDFs and images containing text.

## 9. Optional: use the GUI

Start the GUI with:

```powershell
py -m make_markdown_library gui
```

The GUI lets you choose the source folder, output file, converter mode, Markdown policy, and index format without typing the full `make` command.

## 10. Uninstall later

To remove the tool, see:

- [Uninstall](uninstall.md)

The uninstall command removes the installed Python package. It does not delete the Markdown libraries you created.

## Common Windows problems

### The wheel file cannot be found

Check the filename in Downloads. The version number may be different from the example.

You can also drag the `.whl` file from File Explorer into PowerShell. Windows will paste the full path.

### `py` is not recognized

Install Python first:

- [Install Python on Windows](install-python-windows.md)

Then close and reopen PowerShell.

### `make-markdown-library` is not recognized

Use the Python module form:

```powershell
py -m make_markdown_library --version
```

You can also use the module form for real builds:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" --converter auto
```
