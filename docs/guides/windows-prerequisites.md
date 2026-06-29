# Windows prerequisites

This page is for optional Windows tools that improve conversion quality.

Make Markdown Library itself is installed with the `.whl` file. These tools are separate system programs. You do not need all of them to start.

## What should I install?

| Tool | Required? | Use it when |
| --- | --- | --- |
| Python | Yes | Required to run Make Markdown Library. |
| Tesseract OCR | Recommended for scanned PDFs/images | Your PDFs are scans or your images contain text. |
| LibreOffice | Optional | You want better LiteParse coverage for Word, PowerPoint, Excel, or OpenDocument files. |
| ImageMagick | Optional | You process image formats or image-heavy documents. |
| `lit` CLI | Optional | You want manual LiteParse debugging or CLI-based complexity checks. |

If you mainly use normal PDFs, Word documents, Markdown, and text files, install the tool first and run `doctor`. Add the optional tools only when you need them.

## 1. Check the environment

Run:

```powershell
py -m make_markdown_library doctor
```

The important idea is that `doctor` is advisory. Missing optional tools do not necessarily mean the tool is broken.

## 2. Install Tesseract OCR

Install Tesseract if you want OCR for scanned PDFs or images containing text.

Run:

```powershell
winget install -e --id UB-Mannheim.TesseractOCR
```

Close PowerShell, open a new PowerShell window, then check:

```powershell
tesseract --version
```

Then run:

```powershell
py -m make_markdown_library doctor
```

If `tesseract` is not found after installation, check whether this file exists:

```powershell
Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

If that returns `True`, add the folder to your user PATH:

```powershell
$tesseractPath = "C:\Program Files\Tesseract-OCR"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($currentPath -notlike "*$tesseractPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$tesseractPath", "User")
    Write-Host "Added to User PATH: $tesseractPath"
} else {
    Write-Host "Already in User PATH: $tesseractPath"
}
```

Close PowerShell and open a new one before checking again.

## 3. Install LibreOffice

Install LibreOffice if you want better LiteParse coverage for Office/OpenDocument conversion.

Run:

```powershell
winget install -e --id TheDocumentFoundation.LibreOffice
```

Close PowerShell, open a new PowerShell window, then check:

```powershell
soffice --version
```

If that command does not work but LibreOffice is installed, Make Markdown Library also checks the common Windows install location:

```text
C:\Program Files\LibreOffice\program\soffice.com
```

So a full LibreOffice desktop install can still be detected even when the folder is not on PATH.

## 4. Install ImageMagick

Install ImageMagick only if you process image formats or image-heavy documents.

Run:

```powershell
winget install -e --id ImageMagick.ImageMagick
```

Close PowerShell, open a new PowerShell window, then check:

```powershell
magick -version
```

Important: Windows also has a built-in `convert.exe`. That is not ImageMagick. Make Markdown Library checks for `magick`, not Windows `convert.exe`.

## 5. Check the LiteParse `lit` CLI

The LiteParse Python package may install a `lit` command. It is useful for manual debugging and some CLI-based complexity checks, but it is not required for normal conversion through Python.

Check:

```powershell
lit --help
```

If `lit` is missing but LiteParse is installed, check the user Scripts folder:

```powershell
Get-ChildItem "$env:APPDATA\Python\Python313\Scripts\lit*"
```

If `lit.exe` is there but PowerShell cannot find it, add the folder to your user PATH:

```powershell
$userScripts = "$env:APPDATA\Python\Python313\Scripts"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($currentPath -notlike "*$userScripts*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$userScripts", "User")
    Write-Host "Added to User PATH: $userScripts"
} else {
    Write-Host "Already in User PATH: $userScripts"
}
```

Close PowerShell and open a new one before checking again.

## Recommended setup

For most Windows users, the practical setup is:

1. Install Python.
2. Install Make Markdown Library from the `.whl` file.
3. Install Tesseract if you need OCR.
4. Install LibreOffice only if Office/OpenDocument conversion through LiteParse matters.
5. Install ImageMagick only if image conversion matters.

Use `doctor` after each change:

```powershell
py -m make_markdown_library doctor
```
