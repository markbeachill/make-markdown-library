"""Allow `python -m make_markdown_library` to run the CLI."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
