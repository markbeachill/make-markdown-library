# Install on Windows from the ZIP download

This guide is for people who want to use Make Markdown Library from the public download link.

The important idea is:

> Install the tool once, then point it at any folder of documents.

You do **not** need to install it again for every folder you want to convert.

## 1. Download the ZIP

Open the project download link:

- [Download the latest ZIP](https://github.com/markbeachill/make-markdown-library/archive/refs/heads/main.zip)

Your browser will usually save a file called `make-markdown-library-main.zip` in your Downloads folder.

## 2. Unzip it

Before running any install command, extract the ZIP.

In File Explorer:

1. Find the downloaded `make-markdown-library-main.zip` file. It is often in Downloads.
2. Right-click `make-markdown-library-main.zip`.
3. Choose **Extract All...**.
4. Open the extracted `make-markdown-library-main` folder.

The extracted folder should contain files and folders like these:

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

Then either:

- click the File Explorer address bar, type `powershell`, and press Enter; or
- right-click inside the folder and choose **Open in Terminal**.

Check that PowerShell is in the right folder:

```powershell
Get-ChildItem pyproject.toml
```

If PowerShell lists `pyproject.toml`, continue.

If it says the file cannot be found, you are in the wrong folder. Move into the extracted `make-markdown-library-main` folder and try again.

## 4. Install the tool

Run this command from the extracted folder:

```powershell
py -m pip install .
```

The dot means “install the project in this folder.”

This is a normal install, not an editable developer install. After it finishes, the tool is installed into your Python environment. You do not need to keep running commands from the extracted repository folder.

## 5. Check it works

Try the short command:

```powershell
make-markdown-library --version
```

If Windows says the command is not recognized, use the Python module form instead:

```powershell
py -m make_markdown_library --version
```

Both forms run the same tool.

Then run the diagnostic command:

```powershell
py -m make_markdown_library doctor
```

## 6. Use it on any folder

You can now run the tool from any PowerShell window by giving it the path to the folder you want to convert.

For example, to convert a folder in Documents:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" --converter auto
```

That writes the default outputs in the current PowerShell folder.

To write the library into the same project folder, give an output path:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" -o "C:\Users\Mark\Documents\My Project\markdown-library.md" --converter auto
```

If `markdown-library.md` already exists, choose one safety behaviour.

Keep a backup of the previous output:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" -o "C:\Users\Mark\Documents\My Project\markdown-library.md" --backup-existing
```

Replace the previous output intentionally:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" -o "C:\Users\Mark\Documents\My Project\markdown-library.md" --overwrite
```

## 7. What about the Downloads folder?

It is fine if the ZIP lands in Downloads. Windows users often clear that folder, so the recommended install does **not** depend on keeping the extracted folder there.

Because the recommended command is:

```powershell
py -m pip install .
```

the installed tool is copied into Python. It does not rely on the extracted folder in the same way an editable install does.

After installation succeeds, you can move or delete the extracted `make-markdown-library-main` folder. If you later want to install a newer version, download the ZIP again and run the install command again.

If you prefer to keep the extracted repository for reference, move it somewhere stable such as `C:\Tools\make-markdown-library`, not Downloads.

## 8. Optional: install LiteParse support

LiteParse is optional. Install it only if you want the LiteParse converter/fallback features.

From the extracted repository folder, run:

```powershell
py -m pip install ".[liteparse]"
```

Then run diagnostics again:

```powershell
py -m make_markdown_library doctor
```

## 9. Optional: use the short command

Many Windows Python installs will make this command work:

```powershell
make-markdown-library doctor
```

If it works, you can use `make-markdown-library` instead of `py -m make_markdown_library`.

If it does not work, keep using the module form. It is a little longer, but it avoids Windows PATH problems.

## 10. Optional: use the GUI

Start the GUI with:

```powershell
py -m make_markdown_library gui
```

The GUI lets you choose the source folder, output file, converter mode, Markdown policy, and index format without typing the full `make` command.

## Advanced: virtual environment install

A virtual environment is useful for development or for people who want to isolate Python packages. It is not required for normal use.

The drawback is that a virtual environment has to be activated again in every new PowerShell window before the short command is available. That is why this page does not use it as the default Windows install.

Use a virtual environment only if you already understand why you want one.

Create one:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install into it:

```powershell
python -m pip install .
```

## Common Windows problems

### `py` is not recognized

Install Python from python.org or the Microsoft Store, then reopen PowerShell. During installation, enable the option to add Python to PATH if offered.

### `py -m pip install .` says there is no `pyproject.toml`

You are in the wrong folder, or you are still looking inside the ZIP file. Extract the ZIP, open the extracted folder, and run:

```powershell
Get-ChildItem pyproject.toml
```

If that command does not find the file, move up or down folders until it does.

### `make-markdown-library` is not recognized

Use the Python module form:

```powershell
py -m make_markdown_library --version
```

You can also use the module form for real builds:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" --converter auto
```
