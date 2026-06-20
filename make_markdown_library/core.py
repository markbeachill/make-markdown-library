"""The Make Markdown Library engine.

Plain English: this turns a folder, ZIP, or single file into one tidy Markdown
file that an AI chatbot can read. Each source file becomes a clearly marked
section, so the AI can tell where one source ends and the next begins.

Optionally, it also writes each converted source as its own Markdown file in a
folder, which is handy for storage, diffing, and version control.

Who does what:
- The user collects the source files.
- This engine converts them and writes the library file (and optional split
  files).

Conversion needs MarkItDown, a free tool from Microsoft that converts Word,
PDF, PowerPoint, and other files into Markdown. If MarkItDown is not installed,
this code stops and tells you how to install it.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import re
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

# File types MarkItDown handles well and that make sense as source material.
SUPPORTED_SUFFIXES = {
    ".txt", ".md", ".markdown",
    ".docx", ".doc",
    ".pdf",
    ".pptx", ".ppt",
    ".html", ".htm",
    ".csv",
}

# Neutral defaults for a general-purpose tool.
DEFAULT_SOURCE_DIR = "sources"
DEFAULT_LIBRARY_NAME = "markdown-library.md"

# A strong, unlikely-to-clash marker so the AI can see source boundaries.
DELIMITER = "=" * 70
LIBRARY_METADATA_MARKER = "<!-- markdown-library-file: true -->"


class MarkItDownMissing(RuntimeError):
    """Raised when MarkItDown is not installed. The message says what to do."""


def _require_markitdown():
    """Load MarkItDown, or stop with a clear, friendly message."""
    try:
        from markitdown import MarkItDown  # type: ignore
    except ImportError as exc:
        raise MarkItDownMissing(
            "This needs MarkItDown to read your source files, and it is not "
            "installed yet.\n\n"
            "Command to copy:\n\n"
            "    pip install 'markitdown[all]'\n\n"
            "MarkItDown is a free tool from Microsoft: "
            "https://github.com/microsoft/markitdown"
        ) from exc
    return MarkItDown()


@dataclass
class SourceRecord:
    """One entry in the source manifest.

    Keeps the original file name, path, size, and a checksum (a short
    fingerprint of the file's contents) so the source can be traced later.
    """

    name: str
    relative_path: str
    suffix: str
    size_bytes: int
    checksum: str
    converted: bool
    note: str = ""


@dataclass
class BuildResult:
    """What a build or add produced, so faces can report on it."""

    library_path: Path
    manifest_path: Path
    records: list[SourceRecord] = field(default_factory=list)
    individual_files: list[Path] = field(default_factory=list)

    @property
    def converted_count(self) -> int:
        return sum(1 for r in self.records if r.converted)

    @property
    def skipped_count(self) -> int:
        return sum(1 for r in self.records if not r.converted)


@dataclass
class LibraryCheckReport:
    """A simple structural check of a Markdown library file."""

    library_path: Path
    source_count: int
    duplicate_count: int
    issues: list[str] = field(default_factory=list)

    @property
    def looks_valid(self) -> bool:
        return not self.issues


def _checksum(data: bytes) -> str:
    """Return a short fingerprint of file contents (first 12 hex characters)."""
    return hashlib.sha256(data).hexdigest()[:12]


def _safe_extract_zip(zip_path: Path, extract_to: Path) -> None:
    """Extract a ZIP without allowing paths to escape the target folder."""
    with zipfile.ZipFile(zip_path) as zf:
        root = extract_to.resolve()
        for member in zf.infolist():
            target = (extract_to / member.filename).resolve()
            if not str(target).startswith(str(root)):
                raise zipfile.BadZipFile("ZIP contains an unsafe file path")
        zf.extractall(extract_to)


def _gather_files(source_path: Path, work_dir: Path) -> tuple[list[Path], list[Path]]:
    """Find every usable file, unpacking ZIP files along the way.

    The input can be a single file, a folder, or a ZIP file. Nested ZIPs are
    handled. Returns (found_files, bad_zips) so the caller can report ZIPs that
    could not be opened.
    """
    found: list[Path] = []
    bad_zips: list[Path] = []

    def handle_file(item: Path) -> None:
        if item.suffix.lower() == ".zip":
            extract_to = work_dir / (item.stem + "_unzipped")
            extract_to.mkdir(parents=True, exist_ok=True)
            try:
                _safe_extract_zip(item, extract_to)
            except zipfile.BadZipFile:
                bad_zips.append(item)
                return
            walk(extract_to)
        else:
            found.append(item)

    def walk(directory: Path) -> None:
        for item in sorted(directory.rglob("*")):
            if item.is_dir():
                continue
            handle_file(item)

    if source_path.is_dir():
        walk(source_path)
    elif source_path.is_file():
        handle_file(source_path)
    else:
        raise FileNotFoundError(f"Source not found: {source_path}")
    return found, bad_zips


def _relative_to_source(path: Path, source_path: Path) -> str:
    """Return a useful display path for the manifest and source marker."""
    try:
        base = source_path if source_path.is_dir() else source_path.parent
        return str(path.relative_to(base))
    except ValueError:
        return path.name


def _is_markdown_library_text(text: str) -> bool:
    """Return True if text looks like a Markdown library file."""
    if LIBRARY_METADATA_MARKER in text:
        return True
    return "SOURCE START" in text and "SOURCE END:" in text and "Fingerprint:" in text


def _record_from_imported_section(section: dict[str, str], library_path: Path, source_path: Path) -> SourceRecord:
    """Create a source record for a section imported from another library."""
    file_name = section["file"]
    return SourceRecord(
        name=Path(file_name).name,
        relative_path=file_name,
        suffix=Path(file_name).suffix.lower(),
        size_bytes=0,
        checksum=section.get("fingerprint", ""),
        converted=True,
        note=f"imported from Markdown library: {_relative_to_source(library_path, source_path)}",
    )


def _dedupe_section_pairs(
    section_pairs: list[tuple[SourceRecord, str]],
    *,
    existing_fingerprints: set[str] | None = None,
    allow_duplicates: bool = False,
) -> list[tuple[SourceRecord, str]]:
    """Remove duplicate sections unless the user explicitly allows them."""
    if allow_duplicates:
        return section_pairs

    seen = set(existing_fingerprints or set())
    kept: list[tuple[SourceRecord, str]] = []
    for record, section in section_pairs:
        if record.checksum and record.checksum in seen:
            record.converted = False
            record.note = "not added: duplicate source fingerprint"
            continue
        if record.checksum:
            seen.add(record.checksum)
        kept.append((record, section))
    return kept


def _convert_sources(
    source_path: Path,
    *,
    existing_fingerprints: set[str] | None = None,
    allow_duplicates: bool = False,
) -> tuple[list[SourceRecord], list[tuple[SourceRecord, str]]]:
    """Convert source files and return records plus (record, section) pairs.

    Each section pair also carries the converted body text so the caller can
    optionally write individual files. The body is stored on the record's
    `note` only for skipped files; converted bodies travel in the section text.
    """
    with tempfile.TemporaryDirectory() as tmp:
        work_dir = Path(tmp)
        files, bad_zips = _gather_files(source_path, work_dir)

        records: list[SourceRecord] = []
        section_pairs: list[tuple[SourceRecord, str]] = []
        md = None

        for path in files:
            data = path.read_bytes()
            suffix = path.suffix.lower()

            if suffix in {".md", ".markdown"}:
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    text = data.decode("utf-8", errors="replace")

                if _is_markdown_library_text(text):
                    imported_sections = _parse_library_sections(text)
                    if imported_sections:
                        for section in imported_sections:
                            record = _record_from_imported_section(section, path, source_path)
                            records.append(record)
                            section_pairs.append((record, section["raw"]))
                        continue

            record = SourceRecord(
                name=path.name,
                relative_path=_relative_to_source(path, source_path),
                suffix=suffix,
                size_bytes=len(data),
                checksum=_checksum(data),
                converted=False,
            )

            if suffix not in SUPPORTED_SUFFIXES:
                record.note = "skipped: file type not supported"
                records.append(record)
                continue

            try:
                if md is None:
                    md = _require_markitdown()
                result = md.convert(str(path))
                text = (result.text_content or "").strip()
            except MarkItDownMissing:
                raise
            except Exception as exc:  # noqa: BLE001 - report, do not crash
                record.note = f"skipped: could not convert ({exc})"
                records.append(record)
                continue

            if not text:
                record.note = "skipped: no readable text found"
                records.append(record)
                continue

            record.converted = True
            records.append(record)
            section_pairs.append((record, _format_section(record, text)))

        for bad in bad_zips:
            records.append(SourceRecord(
                name=bad.name,
                relative_path=bad.name,
                suffix=".zip",
                size_bytes=0,
                checksum="",
                converted=False,
                note="skipped: ZIP could not be opened",
            ))

    section_pairs = _dedupe_section_pairs(
        section_pairs,
        existing_fingerprints=existing_fingerprints,
        allow_duplicates=allow_duplicates,
    )
    return records, section_pairs


def _section_body(section: str) -> str:
    """Pull the converted body text back out of a formatted source section."""
    sections = _parse_library_sections(section)
    if sections:
        return _strip_markers(sections[0]["raw"])
    return section


def _strip_markers(raw_section: str) -> str:
    """Return just the readable body of a single source section."""
    match = _SECTION_PATTERN.search(raw_section)
    if match:
        return match.group("body").strip()
    return raw_section.strip()


def _write_individual_files(
    section_pairs: list[tuple[SourceRecord, str]],
    target_dir: Path,
) -> list[Path]:
    """Write each converted source as its own Markdown file. Returns paths."""
    target_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    used: set[str] = set()
    for record, section in section_pairs:
        stem = Path(record.relative_path).stem or "source"
        safe = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-") or "source"
        name = f"{safe}.md"
        counter = 2
        while name in used:
            name = f"{safe}-{counter}.md"
            counter += 1
        used.add(name)
        out = target_dir / name
        body = _section_body(section)
        header = f"<!-- source: {record.relative_path} | fingerprint: {record.checksum} -->\n\n"
        out.write_text(header + body + "\n", encoding="utf-8")
        written.append(out)
    return written


def build_library(
    source_path: str | Path,
    output_path: str | Path | None = None,
    purpose: str = "",
    *,
    title: str = "Markdown Library File",
    allow_duplicates: bool = False,
    individual_files: bool | str | Path = False,
) -> BuildResult:
    """Build a Markdown library file from a file, folder, or ZIP.

    Arguments:
        source_path: a source file, folder, or ZIP file.
        output_path: where to write the library file. Defaults to
            'markdown-library.md' next to the source.
        purpose: an optional one-line note recorded at the top of the library.
        title: the heading to use for the file.
        allow_duplicates: keep sources with repeated fingerprints.
        individual_files: if truthy, also write one Markdown file per source.
            Pass True to use a default folder next to the library, or pass a
            folder path to choose where the split files go.
    """
    source_path = Path(source_path).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source_path}")

    if output_path is None:
        parent = source_path.parent if source_path.is_file() else source_path.parent
        output_path = parent / DEFAULT_LIBRARY_NAME
    output_path = Path(output_path).expanduser().resolve()
    manifest_path = output_path.with_name(output_path.stem + "-manifest.md")

    records, section_pairs = _convert_sources(source_path, allow_duplicates=allow_duplicates)
    sections = [section for _, section in section_pairs]

    _write_library(output_path, purpose, source_path, records, sections, title)
    _write_manifest(manifest_path, purpose, source_path, records)

    written: list[Path] = []
    if individual_files:
        if individual_files is True:
            target_dir = output_path.with_name(output_path.stem + "-files")
        else:
            target_dir = Path(individual_files).expanduser().resolve()
        written = _write_individual_files(section_pairs, target_dir)

    return BuildResult(
        library_path=output_path,
        manifest_path=manifest_path,
        records=records,
        individual_files=written,
    )


def add_to_library(
    library_path: str | Path,
    source_path: str | Path,
    purpose: str = "",
    *,
    skip_duplicates: bool = True,
) -> BuildResult:
    """Add more source files to an existing Markdown library file."""
    library_path = Path(library_path).expanduser().resolve()
    source_path = Path(source_path).expanduser().resolve()

    if not library_path.is_file():
        raise FileNotFoundError(f"Markdown library file not found: {library_path}")
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source_path}")

    existing_text = library_path.read_text(encoding="utf-8")
    existing_sections = _parse_library_sections(existing_text)
    existing_fingerprints = {sec.get("fingerprint", "") for sec in existing_sections}
    manifest_path = library_path.with_name(library_path.stem + "-manifest.md")

    records, section_pairs = _convert_sources(
        source_path,
        existing_fingerprints=existing_fingerprints,
        allow_duplicates=not skip_duplicates,
    )
    sections_to_add = [section for _, section in section_pairs]

    if sections_to_add:
        new_sections: list[dict[str, str]] = []
        for section in sections_to_add:
            new_sections.extend(_parse_library_sections(section))
        all_sections = existing_sections + new_sections
        _write_library_from_sections(library_path, all_sections)
        _write_manifest_from_sections(manifest_path, all_sections)

    return BuildResult(library_path=library_path, manifest_path=manifest_path, records=records)


def list_library_sources(library_path: str | Path) -> list[str]:
    """Return the source names recorded in a Markdown library file."""
    library_path = Path(library_path).expanduser().resolve()
    if not library_path.is_file():
        raise FileNotFoundError(f"Markdown library file not found: {library_path}")
    text = library_path.read_text(encoding="utf-8")
    return re.findall(r"^File: (.+)$", text, flags=re.MULTILINE)


def check_library_format(library_path: str | Path) -> LibraryCheckReport:
    """Check whether a file looks like a valid Markdown library file."""
    library_path = Path(library_path).expanduser().resolve()
    if not library_path.is_file():
        raise FileNotFoundError(f"Markdown library file not found: {library_path}")
    text = library_path.read_text(encoding="utf-8")
    starts = len(re.findall(r"^SOURCE START$", text, flags=re.MULTILINE))
    ends = len(re.findall(r"^SOURCE END:", text, flags=re.MULTILINE))
    fingerprints = re.findall(r"Fingerprint: (\w+)", text)
    duplicate_count = len(fingerprints) - len(set(fingerprints))
    issues: list[str] = []
    if starts == 0:
        issues.append("No SOURCE START markers found.")
    if starts != ends:
        issues.append(f"Source markers do not match: {starts} starts, {ends} ends.")
    if starts != len(fingerprints):
        issues.append("Some source sections may be missing fingerprints.")
    return LibraryCheckReport(
        library_path=library_path,
        source_count=starts,
        duplicate_count=duplicate_count,
        issues=issues,
    )


def remove_file_from_library(library_path: str | Path, selector: str | int) -> BuildResult:
    """Remove one source section from a library by number or filename."""
    library_path = Path(library_path).expanduser().resolve()
    if not library_path.is_file():
        raise FileNotFoundError(f"Markdown library file not found: {library_path}")

    text = library_path.read_text(encoding="utf-8")
    sections = _parse_library_sections(text)
    if not sections:
        raise ValueError("No source sections were found in this Markdown library file.")

    selector_text = str(selector).strip()
    if selector_text.isdigit():
        number = int(selector_text)
        if number < 1 or number > len(sections):
            raise ValueError(f"Source number {number} is out of range. Use `list` to see the numbers.")
        index = number - 1
    else:
        matches = [i for i, sec in enumerate(sections) if sec["file"] == selector_text or Path(sec["file"]).name == selector_text]
        if not matches:
            raise ValueError(f"No source named {selector_text!r} was found. Use `list` to see names.")
        if len(matches) > 1:
            raise ValueError(f"More than one source matched {selector_text!r}. Remove by number instead.")
        index = matches[0]

    removed = sections.pop(index)
    backup_path = library_path.with_name(library_path.stem + ".backup.md")
    backup_path.write_text(text, encoding="utf-8")

    _write_library_from_sections(library_path, sections)
    manifest_path = library_path.with_name(library_path.stem + "-manifest.md")
    _write_manifest_from_sections(manifest_path, sections)

    record = SourceRecord(
        name=Path(removed["file"]).name,
        relative_path=removed["file"],
        suffix=Path(removed["file"]).suffix.lower(),
        size_bytes=0,
        checksum=removed.get("fingerprint", ""),
        converted=True,
        note="removed",
    )
    return BuildResult(library_path=library_path, manifest_path=manifest_path, records=[record])


def _format_section(record: SourceRecord, text: str) -> str:
    """Wrap one converted source in clear start and end markers."""
    header = (
        f"{DELIMITER}\n"
        f"SOURCE START\n"
        f"File: {record.relative_path}\n"
        f"Fingerprint: {record.checksum}\n"
        f"{DELIMITER}\n"
    )
    footer = f"\n{DELIMITER}\nSOURCE END: {record.relative_path}\n{DELIMITER}\n"
    return f"{header}\n{text}\n{footer}"


def _write_library(
    output_path: Path,
    purpose: str,
    source_path: Path,
    records: list[SourceRecord],
    sections: list[str],
    title: str,
) -> None:
    today = _dt.date.today().isoformat()
    converted = [r for r in records if r.converted]
    lines = [
        LIBRARY_METADATA_MARKER,
        f"# {title}",
        "",
        "This file was built by Make Markdown Library from your source files.",
        "Each source below is wrapped in START and END markers so an AI can "
        "tell the sources apart.",
        "",
        f"- Built on: {today}",
        f"- Source input: {source_path.name}",
        f"- Sources included: {len(converted)}",
        f"- Sources skipped: {len(records) - len(converted)}",
    ]
    if purpose:
        lines += ["", f"**Purpose:** {purpose}"]
    lines += ["", "## Source manifest", "", _manifest_table_header()]
    for i, r in enumerate(converted, start=1):
        lines.append(_manifest_row(r, i))
    lines += ["", "---", ""]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n" + "\n".join(sections), encoding="utf-8")


def _write_library_from_sections(output_path: Path, sections: list[dict[str, str]]) -> None:
    """Rewrite a library file from parsed source sections, with a fresh manifest."""
    today = _dt.date.today().isoformat()
    lines = [
        LIBRARY_METADATA_MARKER,
        "# Markdown Library File",
        "",
        "This file was built by Make Markdown Library from your source files.",
        "Each source below is wrapped in START and END markers so an AI can tell the sources apart.",
        "",
        f"- Updated on: {today}",
        f"- Sources included: {len(sections)}",
        "",
        "## Source manifest",
        "",
        _manifest_table_header(),
    ]
    for i, sec in enumerate(sections, start=1):
        record = SourceRecord(
            name=Path(sec["file"]).name,
            relative_path=sec["file"],
            suffix=Path(sec["file"]).suffix.lower(),
            size_bytes=0,
            checksum=sec.get("fingerprint", ""),
            converted=True,
        )
        lines.append(_manifest_row(record, i))
    lines += ["", "---", ""]
    output_path.write_text("\n".join(lines) + "\n" + "\n".join(sec["raw"].rstrip() for sec in sections) + "\n", encoding="utf-8")


def _write_manifest(
    manifest_path: Path,
    purpose: str,
    source_path: Path,
    records: list[SourceRecord],
) -> None:
    """Write a human-readable list of every file we looked at."""
    lines = [
        "# Markdown Library Manifest",
        "",
        "This is a plain list of every file the tool found, and what happened to it.",
        "",
        f"- Source input: {source_path}",
    ]
    if purpose:
        lines += [f"- Purpose: {purpose}"]
    lines += ["", _manifest_table_header()]
    for i, r in enumerate(records, start=1):
        lines.append(_manifest_row(r, i))
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest_from_sections(
    manifest_path: Path,
    sections: list[dict[str, str]],
) -> None:
    """Write a manifest from the source sections currently in a library file."""
    lines = [
        "# Markdown Library Manifest",
        "",
        "This manifest was regenerated from the current Markdown library file.",
        "",
        _manifest_table_header(),
    ]
    for i, sec in enumerate(sections, start=1):
        record = SourceRecord(
            name=Path(sec["file"]).name,
            relative_path=sec["file"],
            suffix=Path(sec["file"]).suffix.lower(),
            size_bytes=0,
            checksum=sec.get("fingerprint", ""),
            converted=True,
        )
        lines.append(_manifest_row(record, i))
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _manifest_table_header() -> str:
    return "| No. | File | Type | Size (bytes) | Fingerprint | Status |\n| ---: | --- | --- | ---: | --- | --- |"


def _manifest_row(record: SourceRecord, number: int) -> str:
    status = "included" if record.converted else (record.note or "skipped")
    size = record.size_bytes if record.size_bytes else ""
    return (
        f"| {number} | {record.relative_path} | {record.suffix or ''} | "
        f"{size} | {record.checksum} | {status} |"
    )


_SECTION_PATTERN = re.compile(
    rf"{re.escape(DELIMITER)}\nSOURCE START\nFile: (?P<file>.*?)\nFingerprint: (?P<fingerprint>.*?)\n{re.escape(DELIMITER)}\n(?P<body>.*?)\n{re.escape(DELIMITER)}\nSOURCE END: .*?\n{re.escape(DELIMITER)}",
    flags=re.DOTALL,
)


def _parse_library_sections(text: str) -> list[dict[str, str]]:
    """Return source sections from a Markdown library file."""
    sections: list[dict[str, str]] = []
    for match in _SECTION_PATTERN.finditer(text):
        sections.append({
            "file": match.group("file").strip(),
            "fingerprint": match.group("fingerprint").strip(),
            "raw": match.group(0),
        })
    return sections
