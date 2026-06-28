"""Command line for Make Markdown Library."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import (
    DEFAULT_CONVERTER_MODE,
    DEFAULT_INDEX_FORMAT,
    DEFAULT_LIBRARY_NAME,
    DEFAULT_MARKDOWN_POLICY,
    DEFAULT_SOURCE_DIR,
    ConversionDependencyMissing,
    OptionalDependencyMissing,
    OutputSafetyError,
    add_to_library,
    build_library,
    check_library_format,
    diagnose_environment,
    install_optional_tool,
    list_library_sources,
    plan_rebuild,
    rebuild_library,
    remove_file_from_library,
)


def _print_not_added(records) -> None:
    for record in records:
        if record.note.startswith("not added:"):
            print(f"  not added - {record.relative_path}")


def _print_build_result(result) -> None:
    print(f"  Library:  {result.library_path}")
    print(f"  Manifest: {result.manifest_path}")
    if result.index_path:
        print(f"  JSON index: {result.index_path}")
    if result.yaml_index_path:
        print(f"  YAML index: {result.yaml_index_path}")
    print(f"  Sources included: {result.converted_count}")
    print(f"  Sources skipped:  {result.skipped_count}")
    if result.individual_files:
        print(f"  Individual files: {len(result.individual_files)} in {result.individual_files[0].parent}")


def _liteparse_options_from_args(args: argparse.Namespace) -> dict[str, object]:
    return {
        "image_mode": getattr(args, "liteparse_image_mode", "placeholder"),
        "extract_links": not getattr(args, "liteparse_no_links", False),
        "ocr": not getattr(args, "liteparse_no_ocr", False),
        "ocr_language": getattr(args, "liteparse_ocr_language", "eng"),
        "target_pages": getattr(args, "liteparse_target_pages", None),
        "dpi": getattr(args, "liteparse_dpi", 150),
        "max_pages": getattr(args, "liteparse_max_pages", None),
        "password": getattr(args, "liteparse_password", None),
        "complexity_check": getattr(args, "liteparse_complexity_check", False),
    }


def _result_summary(result) -> dict[str, object]:
    return {
        "library": str(result.library_path),
        "manifest": str(result.manifest_path),
        "json_index": str(result.index_path) if result.index_path else None,
        "yaml_index": str(result.yaml_index_path) if result.yaml_index_path else None,
        "sources_included": result.converted_count,
        "sources_skipped": result.skipped_count,
        "individual_files": [str(p) for p in result.individual_files],
    }


def _print_verbose_records(records) -> None:
    for record in records:
        print(f"  {record.relative_path}")
        print(f"    status: {'included' if record.converted else 'skipped'}")
        if record.converter:
            print(f"    converter: {record.converter}")
        if record.fallback_used:
            print(f"    fallback: {record.fallback_from} -> {record.fallback_to} ({record.fallback_reason})")
        if record.complexity_checked:
            print(f"    complexity: {'complex' if record.complexity_complex else 'simple'} ({record.complexity_reason})")
        if record.note:
            print(f"    note: {record.note}")


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
    source, out = _resolve_paths(args.paths, args.output)
    individual = args.individual_dir or args.individual_files
    try:
        result = build_library(
            source,
            out,
            purpose=args.purpose or "",
            allow_duplicates=args.allow_duplicates,
            individual_files=individual,
            converter_mode=args.converter,
            markdown_policy=args.md_policy,
            include_generated=args.include_generated,
            index_format=args.index_format,
            index_path=args.index_path,
            liteparse_options=_liteparse_options_from_args(args),
            overwrite=args.overwrite,
            backup_existing=args.backup_existing,
            clean_individual_dir=args.clean_individual_dir,
            overwrite_individual=args.overwrite_individual,
            allow_individual_in_source=args.allow_individual_in_source,
        )
    except (FileNotFoundError, NotADirectoryError, OutputSafetyError) as exc:
        print(f"Problem: {exc}", file=sys.stderr)
        return 1
    except (ConversionDependencyMissing, OptionalDependencyMissing) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.summary_json:
        print(json.dumps(_result_summary(result), indent=None if args.quiet else 2))
        return 0
    if not args.quiet:
        print("Done. Markdown library created.")
        _print_build_result(result)
        if args.verbose:
            _print_verbose_records(result.records)
        _print_not_added(result.records)
    return 0


def _cmd_rebuild(args: argparse.Namespace) -> int:
    try:
        if args.dry_run:
            plan = plan_rebuild(
                args.index,
                converter_mode=args.converter,
                markdown_policy=args.md_policy,
                liteparse_options=_liteparse_options_from_args(args),
            )
            if args.summary_json:
                print(json.dumps(plan, indent=None if args.quiet else 2))
            elif not args.quiet:
                counts = plan["counts"]
                print(f"Would rebuild {counts['would_rebuild']} changed files.")
                print(f"Would skip {counts['would_skip']} unchanged files.")
                print(f"Would remove {counts['would_remove']} missing sources.")
                changes = plan.get("setting_changes") or []
                if changes:
                    print("Setting changes force rebuild: " + ", ".join(changes))
            return 0

        result = rebuild_library(
            args.index,
            output_path=args.output,
            converter_mode=args.converter,
            markdown_policy=args.md_policy,
            index_format=args.index_format,
            liteparse_options=_liteparse_options_from_args(args),
            overwrite=args.overwrite,
            backup_existing=not args.no_backup_existing,
            clean_individual_dir=args.clean_individual_dir,
            overwrite_individual=args.overwrite_individual,
            allow_individual_in_source=args.allow_individual_in_source,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Problem: {exc}", file=sys.stderr)
        return 1
    except (ConversionDependencyMissing, OptionalDependencyMissing) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.summary_json:
        print(json.dumps(_result_summary(result), indent=None if args.quiet else 2))
        return 0
    if not args.quiet:
        print("Done. Markdown library rebuilt from index.")
        _print_build_result(result)
        if args.verbose:
            _print_verbose_records(result.records)
        reused = sum(1 for r in result.records if "reused unchanged" in r.note)
        if reused:
            print(f"  Reused unchanged sections: {reused}")
    return 0


def _cmd_add(args: argparse.Namespace) -> int:
    try:
        result = add_to_library(
            args.library,
            args.source,
            purpose=args.purpose or "",
            skip_duplicates=not args.allow_duplicates,
            converter_mode=args.converter,
            markdown_policy=args.md_policy,
            include_generated=args.include_generated,
            index_format=args.index_format,
            liteparse_options=_liteparse_options_from_args(args),
            backup_existing=not args.no_backup_existing,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Problem: {exc}", file=sys.stderr)
        return 1
    except (ConversionDependencyMissing, OptionalDependencyMissing) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if result.converted_count:
        print("Done. Source files added.")
    else:
        print("No new source sections were added.")
    _print_build_result(result)
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
        return 0
    for i, name in enumerate(sources, start=1):
        print(f"{i}. {name}")
    return 0


def _cmd_remove(args: argparse.Namespace) -> int:
    try:
        result = remove_file_from_library(args.library, args.selector, index_format=args.index_format)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Problem: {exc}", file=sys.stderr)
        return 1
    print("Done. Source removed.")
    print(f"  Library:  {result.library_path}")
    print(f"  Manifest: {result.manifest_path}")
    if result.index_path:
        print(f"  JSON index: {result.index_path}")
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


def _cmd_doctor(_args: argparse.Namespace) -> int:
    print("Make Markdown Library environment check")
    for status in diagnose_environment():
        flag = "OK" if status.available else "MISSING"
        detail = status.version or status.path or status.note
        print(f"  {flag:7} {status.name:14} {detail}")
        if not status.available and status.install_command:
            print(f"          install: {status.install_command}")
    return 0


def _cmd_setup(args: argparse.Namespace) -> int:
    try:
        return install_optional_tool(args.tool, yes=args.yes)
    except ValueError as exc:
        print(f"Problem: {exc}", file=sys.stderr)
        return 1


def _cmd_gui(_args: argparse.Namespace) -> int:
    from .gui import main as gui_main
    return gui_main()


def _add_conversion_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--converter",
        choices=["markitdown", "liteparse", "auto", "hybrid"],
        default=DEFAULT_CONVERTER_MODE,
        help="Converter strategy. Default keeps existing behaviour: markitdown.",
    )
    parser.add_argument(
        "--md-policy",
        choices=["include", "import-libs", "skip"],
        default=DEFAULT_MARKDOWN_POLICY,
        help="How to handle .md files already in the folder.",
    )
    parser.add_argument(
        "--include-generated",
        action="store_true",
        help="Include generated manifests, indexes, and split Markdown files instead of skipping them.",
    )
    parser.add_argument(
        "--index-format",
        choices=["json", "yaml", "both", "none"],
        default=DEFAULT_INDEX_FORMAT,
        help="Machine-readable index output. JSON is the default.",
    )
    _add_liteparse_options(parser)


def _add_liteparse_options(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group("LiteParse options")
    group.add_argument("--liteparse-image-mode", choices=["off", "placeholder", "markdown", "base64"], default="placeholder")
    group.add_argument("--liteparse-no-links", action="store_true", help="Disable link extraction when LiteParse is used.")
    group.add_argument("--liteparse-no-ocr", action="store_true", help="Disable OCR when LiteParse is used.")
    group.add_argument("--liteparse-ocr-language", default="eng", help="OCR language code for LiteParse. Default: eng.")
    group.add_argument("--liteparse-target-pages", help="Pages to parse, e.g. 1,2,5-8.")
    group.add_argument("--liteparse-dpi", type=int, default=150, help="Rasterization DPI for LiteParse OCR/layout work.")
    group.add_argument("--liteparse-max-pages", type=int, help="Limit pages parsed by LiteParse.")
    group.add_argument("--liteparse-password", help="Password for protected documents. Not written to indexes.")
    group.add_argument("--liteparse-complexity-check", action="store_true", help="Use `lit is-complex` to prefer LiteParse for scanned/complex PDFs.")


def _add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--verbose", action="store_true", help="Print per-file routing and fallback details.")
    parser.add_argument("--quiet", action="store_true", help="Only print errors unless --summary-json is used.")
    parser.add_argument("--summary-json", action="store_true", help="Print a machine-readable command summary.")


def _add_safety_options(parser: argparse.ArgumentParser, *, for_rebuild: bool = False) -> None:
    group = parser.add_argument_group("Safety and overwrite options")
    group.add_argument("--overwrite", action="store_true", help="Replace existing library/manifest/index outputs without making backups.")
    if for_rebuild:
        group.add_argument("--no-backup-existing", action="store_true", help="Do not back up existing outputs before rebuild. Existing outputs then require --overwrite.")
    else:
        group.add_argument("--backup-existing", action="store_true", help="Back up existing library/manifest/index outputs before replacing them.")
    group.add_argument("--clean-individual-dir", action="store_true", help="Remove old generated split Markdown files before writing new ones.")
    group.add_argument("--overwrite-individual", action="store_true", help="Allow split Markdown outputs to overwrite non-generated Markdown files.")
    group.add_argument("--allow-individual-in-source", action="store_true", help="Allow --individual-dir to be exactly the source folder.")


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
    p_make.add_argument("--index-path", help="Custom JSON index path. Used with --index-format json or both.")
    _add_conversion_options(p_make)
    _add_safety_options(p_make)
    _add_output_options(p_make)
    p_make.set_defaults(func=_cmd_make)

    p_rebuild = sub.add_parser("rebuild", help="Rebuild a library from a previous JSON index, reusing unchanged sections.")
    p_rebuild.add_argument("index", help="The .index.json file to rebuild from.")
    p_rebuild.add_argument("-o", "--output", help="Optional replacement output library path.")
    p_rebuild.add_argument("--converter", choices=["markitdown", "liteparse", "auto", "hybrid"], default=None)
    p_rebuild.add_argument("--md-policy", choices=["include", "import-libs", "skip"], default=None)
    p_rebuild.add_argument("--index-format", choices=["json", "yaml", "both", "none"], default=DEFAULT_INDEX_FORMAT)
    p_rebuild.add_argument("--dry-run", action="store_true", help="Show what would rebuild without writing files.")
    _add_liteparse_options(p_rebuild)
    _add_safety_options(p_rebuild, for_rebuild=True)
    _add_output_options(p_rebuild)
    p_rebuild.set_defaults(func=_cmd_rebuild)

    p_add = sub.add_parser("add", help="Add sources to an existing library file.")
    p_add.add_argument("library", help="The existing Markdown library file.")
    p_add.add_argument("source", help="A new file, folder, ZIP, or library to add.")
    p_add.add_argument("-p", "--purpose", help="A short note about why you are adding these.")
    p_add.add_argument("--allow-duplicates", action="store_true", help="Add even when fingerprints already exist.")
    p_add.add_argument("--no-backup-existing", action="store_true", help="Do not create backups before modifying the existing library.")
    _add_conversion_options(p_add)
    p_add.set_defaults(func=_cmd_add)

    p_list = sub.add_parser("list", help="List the sources in a library file.")
    p_list.add_argument("library", help="The library file to inspect.")
    p_list.set_defaults(func=_cmd_list)

    p_remove = sub.add_parser("remove-file", help="Remove one source by list number or filename.")
    p_remove.add_argument("library", help="The library file to edit.")
    p_remove.add_argument("selector", help="The source number from `list`, or the filename.")
    p_remove.add_argument("--index-format", choices=["json", "yaml", "both", "none"], default=DEFAULT_INDEX_FORMAT)
    p_remove.set_defaults(func=_cmd_remove)

    p_check = sub.add_parser("check-file", help="Check a library file's structure.")
    p_check.add_argument("library", help="The library file to check.")
    p_check.set_defaults(func=_cmd_check)

    p_doctor = sub.add_parser("doctor", help="Check converters and optional dependencies.")
    p_doctor.set_defaults(func=_cmd_doctor)

    p_setup = sub.add_parser("setup", help="Install optional converter support using this Python environment.")
    p_setup.add_argument("tool", choices=["markitdown", "liteparse", "yaml", "all-converters"])
    p_setup.add_argument("--yes", "-y", action="store_true", help="Do not ask for confirmation before installing.")
    p_setup.set_defaults(func=_cmd_setup)

    p_gui = sub.add_parser("gui", help="Open the click-to-use window.")
    p_gui.set_defaults(func=_cmd_gui)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
