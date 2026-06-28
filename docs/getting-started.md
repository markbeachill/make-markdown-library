# Getting started

This page gives the shortest path from install to a first Markdown library.

## 1. Install the tool

On Windows, start here:

- [Install on Windows](guides/windows-install.md)

If Python is not installed yet, use this page first:

- [Install Python on Windows](guides/install-python-windows.md)

The normal Windows install uses the release wheel package. You do not need to download or keep the GitHub source repository to use the tool.

## 2. Check the install

Run:

```powershell
py -m make_markdown_library --version
```

Then run diagnostics:

```powershell
py -m make_markdown_library doctor
```

## 3. Pick a folder to convert

The source folder is the folder containing documents you want to turn into a Markdown library.

Example source folder:

```text
C:\Users\Mark\Documents\My Project
```

You do not install the tool into this folder. You point the installed command at it.

## 4. Create a first library

Run:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" --converter auto
```

This writes the default outputs in the current PowerShell folder.

To write the library inside the project folder, run:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" -o "C:\Users\Mark\Documents\My Project\markdown-library.md" --converter auto
```

## 5. Look at the outputs

A successful build creates files such as:

```text
markdown-library.md
markdown-library-manifest.md
markdown-library.index.json
```

If you enable individual files, it can also create:

```text
markdown-library-files/
```

See [Output reference](output-reference.md) for the full list.

## 6. Re-running safely

If the output library already exists, `make` refuses to overwrite it unless you choose one of the safety options.

Keep a backup:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" -o "C:\Users\Mark\Documents\My Project\markdown-library.md" --backup-existing
```

Replace intentionally:

```powershell
py -m make_markdown_library make "C:\Users\Mark\Documents\My Project" -o "C:\Users\Mark\Documents\My Project\markdown-library.md" --overwrite
```

See [Processing rules](processing-rules.md) for the exact contract.
