"""Command line for Make Markdown Library.

This is the terminal face. It does no conversion itself; it calls `core` and
reports the result. The GUI face does the same.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import (
    DEFAULT_LIBRARY_NAME,
    DEFAULT_SOURCE_DIR,
    MarkItDownMissing,
    add_to_library,
    build_library,
    check_library_format,
    list_library_sources,
    remove_file_from_library,
)


def _print_not_added(records) -> None:
    for record in records:
        if record.note.startswith("not added:"):
            print(f"  not added - {record.relative_path}")


def _resolve_paths(paths: list[str], output: str | None) -> tuple[str, str]:
    if output and len(paths) > 1:
        raise SystemExit("Problem: use either a destination path or --output, not both.")
    if len(paths) > 2:
        raise SystemExit("Problem: too many paths were given.")
    source = paths[0] if paths else DEFAULT_SOURCE_DIR
    if output:
        out = output
    elif len(paths) == 2:
        destination = Path(paths[1])
        if destination.suffix.lower() in {".md", ".markdown"}:
            out = str(destination)
        else:
            out = str(destination / DEFAULT_LIBRARY_NAME)
    else:
        out = DEFAULT_LIBRARY_NAME
    return source, out


def _cmd_make(args: argparse.Namespace) -> int:
    try:
        source, output = _resolve_paths(list(args.paths), args.output)
        individual: bool | str = args.individual_files or False
        if args.individual_dir:
            individual = args.individual_dir
        result = build_library(
            source,
            output,
            args.purpose or "",
            allow_duplicates=args.allow_duplicates,
            individual_files=individual,
        )
    except MarkItDownMissing as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"Problem: {exc}", file=sys.stderr)
        return 1

    print("Markdown library file made.")
    print(f"  Library:  {result.library_path}")
    print(f"  Manifest: {result.manifest_path}")
    print(f"  Sources included: {result.converted_count}")
    print(f"  Sources skipped:  {result.skipped_count}")
    if result.individual_files:
        print(f"  Individual files: {len(result.individual_files)} in {result.individual_files[0].parent}")
    if result.skipped_count:
        _print_not_added(result.records)
        print("  Read the manifest to see why some files were skipped.")
    return 0


def _cmd_add(args: argparse.Namespace) -> int:
    try:
        result = add_to_library(
            args.library,
            args.source,
            args.purpose or "",
            skip_duplicates=not args.allow_duplicates,
        )
    except MarkItDownMissing as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"Problem: {exc}", file=sys.stderr)
        return 1

    print("Sources added to Markdown library file.")
    print(f"  Library:  {result.library_path}")
    print(f"  Sources added:   {result.converted_count}")
    print(f"  Sources skipped: {result.skipped_count}")
    if result.skipped_count:
        _print_not_added(result.records)
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    try:
        sources = list_library_sources(args.library)
    except FileNotFoundError as exc:
        print(f"Problem: {exc}", file=sys.stderr)
        return 1
    if not sources:
        print("No sources found in this library file.")
        return 1
    print(f"Sources in {args.library}:")
    for idx, source in enumerate(sources, start=1):
        print(f"  {idx}. {source}")
    return 0


def _cmd_remove(args: argparse.Namespace) -> int:
    try:
        result = remove_file_from_library(args.library, args.selector)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Problem: {exc}", file=sys.stderr)
        return 1
    removed = result.records[0].relative_path if result.records else args.selector
    print("Source removed from Markdown library file.")
    print(f"  Removed:  {removed}")
    print(f"  Library:  {result.library_path}")
    print("  A backup was saved next to the library file.")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    try:
        report = check_library_format(args.library)
    except FileNotFoundError as exc:
        print(f"Problem: {exc}", file=sys.stderr)
        return 1
    print("Markdown library file check done.")
    print(f"  Sources: {report.source_count}")
    print(f"  Duplicate fingerprints: {report.duplicate_count}")
    if report.issues:
        print("  Problems found:")
        for issue in report.issues:
            print(f"  - {issue}")
        return 1
    print("  The file has the expected source markers.")
    return 0


def _cmd_gui(_args: argparse.Namespace) -> int:
    from .gui import main as gui_main
    return gui_main()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="make-markdown-library",
        description="Make one structured Markdown library file from source files.",
    )
    parser.add_argument("--version", action="version", version=f"make-markdown-library {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_make = sub.add_parser("make", help=f"Make a library from a folder, file, or ZIP. Default: {DEFAULT_SOURCE_DIR}/ -> {DEFAULT_LIBRARY_NAME}")
    p_make.add_argument("paths", nargs="*", metavar="path", help="Optional source folder and destination folder/file.")
    p_make.add_argument("-o", "--output", help="Where to save the library file. Do not use with a destination path.")
    p_make.add_argument("-p", "--purpose", help="A short note about what this library is for.")
    p_make.add_argument("--allow-duplicates", action="store_true", help="Add sources even when fingerprints repeat.")
    p_make.add_argument("--individual-files", action="store_true", help="Also write one Markdown file per source.")
    p_make.add_argument("--individual-dir", help="Folder for the individual files. Implies --individual-files.")
    p_make.set_defaults(func=_cmd_make)

    p_add = sub.add_parser("add", help="Add sources to an existing library file.")
    p_add.add_argument("library", help="The existing Markdown library file.")
    p_add.add_argument("source", help="A new file, folder, ZIP, or library to add.")
    p_add.add_argument("-p", "--purpose", help="A short note about why you are adding these.")
    p_add.add_argument("--allow-duplicates", action="store_true", help="Add even when fingerprints already exist.")
    p_add.set_defaults(func=_cmd_add)

    p_list = sub.add_parser("list", help="List the sources in a library file.")
    p_list.add_argument("library", help="The library file to inspect.")
    p_list.set_defaults(func=_cmd_list)

    p_remove = sub.add_parser("remove-file", help="Remove one source by list number or filename.")
    p_remove.add_argument("library", help="The library file to edit.")
    p_remove.add_argument("selector", help="The source number from `list`, or the filename.")
    p_remove.set_defaults(func=_cmd_remove)

    p_check = sub.add_parser("check-file", help="Check a library file's structure.")
    p_check.add_argument("library", help="The library file to check.")
    p_check.set_defaults(func=_cmd_check)

    p_gui = sub.add_parser("gui", help="Open the click-to-use window.")
    p_gui.set_defaults(func=_cmd_gui)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
