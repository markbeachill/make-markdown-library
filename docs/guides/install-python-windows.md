# Install Python on Windows

Make Markdown Library is a Python tool. Before installing it, check whether Python is already available.

## 1. Check Python

Open PowerShell and run this command:

```powershell
py --version
```

If you see a Python version, continue to [Install on Windows](windows-install.md).

If Windows says `py` is not recognized, install Python first.

## 2. Install Python

Use the official Python download page:

- [Download Python for Windows](https://www.python.org/downloads/)

Download the current Windows installer and run it.

During installation, choose the option that installs the Python launcher. If the installer offers an option to add Python to PATH, enabling it is helpful, but Make Markdown Library uses the `py` launcher so PATH is less important.

## 3. Open a new PowerShell window

After installing Python, close PowerShell and open a new PowerShell window.

Run this command again:

```powershell
py --version
```

If it prints a version, Python is ready.

## 4. Check pip

Run this command:

```powershell
py -m pip --version
```

If pip prints a version, continue to [Install on Windows](windows-install.md).

If pip is missing, repair or reinstall Python from python.org and make sure pip is included.

## What Python is used for

Python installs and runs the Make Markdown Library command. Once the tool is installed, you can run it against any folder of documents.

You do not install Make Markdown Library into each document folder. You install it once into Python, then point it at the folder you want to convert.
