# Getting started

Install the project in editable mode during development:

```bash
pip install -e .
```

Create a library:

```bash
make-markdown-library make sources -o markdown-library.md
```

Use automatic routing and write split files:

```bash
make-markdown-library make sources -o markdown-library.md --converter auto --individual-files
```

Open the GUI:

```bash
python -m make_markdown_library gui
```

Check optional dependencies:

```bash
make-markdown-library doctor
```
