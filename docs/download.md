# Download Make Markdown Library

Use this page if you want to install the tool. You do **not** need to download the source repository to use Make Markdown Library.

## Recommended download

Download the Python installer package:

- [Download installer: `make_markdown_library-0.4.0-py3-none-any.whl`](https://github.com/markbeachill/make-markdown-library/releases/download/v0.4.0/make_markdown_library-0.4.0-py3-none-any.whl)

This is the file used by the Windows install guide. Your browser may not know how to open a `.whl` file. That is normal. Do **not** double-click it. Install it from PowerShell.

## Install after downloading

If the file is in your Downloads folder, run this in PowerShell:

```powershell
py -m pip install --user "$env:USERPROFILE\Downloads\make_markdown_library-0.4.0-py3-none-any.whl"
```

Then check the install:

```powershell
py -m make_markdown_library --version
```

For the full step-by-step Windows instructions, use:

- [Install on Windows](guides/windows-install.md)

## Alternative: open the GitHub release page

If the direct installer link does not work, open the release page and download the `.whl` file from the **Assets** section:

- [Open release v0.4.0](https://github.com/markbeachill/make-markdown-library/releases/tag/v0.4.0)
- [Open latest release](https://github.com/markbeachill/make-markdown-library/releases/latest)

The release page also shows GitHub’s automatic source-code downloads. Those are for developers. Normal users should choose the `.whl` installer file.

## What should I download?

| File | Use it for |
| --- | --- |
| `make_markdown_library-0.4.0-py3-none-any.whl` | Installing the tool |
| `Source code (zip)` | Reading or modifying the repository source |
| `Source code (tar.gz)` | Reading or modifying the repository source on Unix-like systems |

## After installation

You can delete the downloaded `.whl` file after installation. The tool is installed into Python’s user package area, not into your Downloads folder.
