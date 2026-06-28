# Uninstall

Uninstalling removes the installed Make Markdown Library Python package. It does not delete any Markdown libraries, manifests, indexes, or source documents you created.

## Windows

Open PowerShell and run:

```powershell
py -m pip uninstall make-markdown-library
```

Pip will ask for confirmation. Type `y` and press Enter.

Check that it has gone:

```powershell
py -m make_markdown_library --version
```

If Windows says the module cannot be found, the uninstall worked.

## macOS or Linux

Run:

```bash
python3 -m pip uninstall make-markdown-library
```

Confirm with `y` when pip asks.

## If you installed LiteParse separately

Make Markdown Library does not automatically uninstall optional converter packages that you installed separately.

To remove LiteParse as well, run:

```powershell
py -m pip uninstall liteparse
```

On macOS or Linux, run:

```bash
python3 -m pip uninstall liteparse
```

## What uninstall does not delete

Uninstall does not delete:

- source folders;
- generated `markdown-library.md` files;
- manifest files;
- JSON/YAML index files;
- individual Markdown output folders;
- downloaded wheel files in Downloads.

You can delete downloaded installer files manually after installation or uninstallation.

## Reinstalling later

Download the installer again from [Download Make Markdown Library](../download.md), then install it:

```powershell
py -m pip install --user "$env:USERPROFILE\Downloads\make_markdown_library-0.3.8-py3-none-any.whl"
```

If the filename has a newer version number, use that filename instead.
