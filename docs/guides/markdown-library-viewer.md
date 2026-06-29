# Markdown Library Viewer

The Markdown Library Viewer is a small read-only viewer for opening Markdown files in a browser.

It is designed for two simple cases:

- open any ordinary `.md` file and read it as formatted Markdown;
- open a Make Markdown Library file and browse its source sections from a left-hand index.

The viewer does not upload your file. The file is read locally by your browser after you choose it.

## Easiest option: use the website viewer

Open the viewer page on the documentation site.

```text
https://markbeachill.github.io/make-markdown-library/viewer/
```

Then choose your `markdown-library.md` file from your computer.

The website viewer works because generated libraries include viewer metadata in the Markdown file itself. It does not need the separate JSON index for basic browsing.

## Offline option: download one HTML file

Download this file:

```text
view-markdown-library.html
```

Then double-click it to open it in your browser.

This is the simplest portable viewer. It does not need Python, Node, Git, Tauri, Electron, or an installer.

## What the viewer expects

For full library navigation, the Markdown file should have been created by Make Markdown Library 0.4.0 or later. New libraries include:

- YAML front matter at the top of the file;
- a list of source documents for the left-hand index;
- hidden `mmlib:source-start` and `mmlib:source-end` comments around each source section.

The external `markdown-library.index.json` file is still useful for rebuilds and metadata, but the viewer does not require it for basic browsing.

## How to use it

Open the viewer.

Click **Open Markdown file**.

Choose your generated library file, usually:

```text
markdown-library.md
```

If the file is a library, the source list appears on the left. Click a source to read that section on the right.

If the file is an ordinary Markdown file, the viewer renders the whole file as one document.

## Viewer controls

| Control | Purpose |
| --- | --- |
| Open Markdown file | Choose a `.md` file from your computer |
| Search sources | Filter the left-hand source list |
| Show raw / Show formatted | Switch between formatted Markdown and raw Markdown |
| Copy section | Copy the currently selected Markdown section |

## Limitations

The viewer is read-only. It does not edit Markdown files.

The viewer does not automatically open neighbouring files from your computer. That is a browser security rule. Because new libraries contain the source index inside the Markdown file, the viewer usually only needs the one `.md` file.

Old libraries created before 0.4.0 may not show a left-hand index. Rebuild the library with a current Make Markdown Library version to add viewer metadata.
