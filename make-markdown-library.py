#!/usr/bin/env python3
"""Compatibility launcher for Make Markdown Library.

The implementation now lives in the installable package under
`make_markdown_library/` so the CLI, GUI, tests, and library API all share one
engine. Keep this file for people who are used to running:

    python make-markdown-library.py ...

Examples:

    python make-markdown-library.py gui
    python make-markdown-library.py make sources -o markdown-library.md
    python make-markdown-library.py setup liteparse
"""

from __future__ import annotations

import sys
from pathlib import Path

# Let this launcher work from a source checkout without installation.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from make_markdown_library.cli import main
except ImportError as exc:  # pragma: no cover - only for broken local copies
    print("Could not import the make_markdown_library package next to this file.", file=sys.stderr)
    print("Run from a full repository checkout or install with: pip install -e .", file=sys.stderr)
    raise SystemExit(1) from exc


if __name__ == "__main__":
    # Preserve the old double-click behaviour: no arguments opens the GUI.
    args = sys.argv[1:] or ["gui"]
    raise SystemExit(main(args))
