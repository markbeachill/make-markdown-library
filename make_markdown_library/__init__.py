"""Make Markdown Library.

Turn a folder of mixed files (Word, PDF, PowerPoint, Markdown, HTML, CSV,
ZIPs) into one structured Markdown library file an AI chatbot can read, and
optionally write each converted source as its own Markdown file.

This package has one engine (`core`) and two faces on top of it:

- `cli`  - the command line, for people comfortable with a terminal.
- `gui`  - a small Tkinter window, for people who would rather click.

Both faces call the same `core` functions. No conversion logic lives in the
faces.
"""

__version__ = "0.3.0"
