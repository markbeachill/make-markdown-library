"""The Make Markdown Library engine.

Plain English: this turns a folder, ZIP, or single file into one tidy Markdown
file that an AI chatbot can read. Each source file becomes a clearly marked
section, so the AI can tell where one source ends and the next begins.

The engine is intentionally independent from the CLI and GUI. It supports:

- pluggable converters (MarkItDown, LiteParse, or automatic routing);
- direct handling of Markdown files that are already Markdown;
- safe ZIP extraction;
- duplicate detection;
- optional per-source Markdown files; and
- machine-readable JSON/YAML index files for automation and rebuilds.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import importlib.metadata as _metadata
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

# File types that make sense as source material. Some are read directly, some
# go through MarkItDown, and some can optionally go through LiteParse.
MARKDOWN_SUFFIXES = {".md", ".markdown"}
DIRECT_TEXT_SUFFIXES = {".txt", ".csv", ".json", ".jsonl", ".xml", ".log"}
MARKITDOWN_SUFFIXES = {
    ".doc", ".docx",
    ".ppt", ".pptx",
    ".xls", ".xlsx",
    ".pdf",
    ".html", ".htm",
    ".rtf",
    *DIRECT_TEXT_SUFFIXES,
}
LITEPARSE_SUFFIXES = {
    ".pdf",
    ".doc", ".docx",
    ".ppt", ".pptx",
    ".xls", ".xlsx",
    ".odt", ".ods", ".odp",
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp",
}
SUPPORTED_SUFFIXES = MARKDOWN_SUFFIXES | MARKITDOWN_SUFFIXES | LITEPARSE_SUFFIXES

ConverterMode = Literal["markitdown", "liteparse", "auto", "hybrid"]
MarkdownPolicy = Literal["include", "import-libs", "skip"]
IndexFormat = Literal["json", "yaml", "both", "none"]

# Neutral defaults for a general-purpose tool.
DEFAULT_SOURCE_DIR = "sources"
DEFAULT_LIBRARY_NAME = "markdown-library.md"
DEFAULT_CONVERTER_MODE: ConverterMode = "markitdown"
DEFAULT_MARKDOWN_POLICY: MarkdownPolicy = "include"
DEFAULT_INDEX_FORMAT: IndexFormat = "json"

# A strong, unlikely-to-clash marker so the AI can see source boundaries.
DELIMITER = "=" * 70
LIBRARY_METADATA_MARKER = "<!-- markdown-library-file: true -->"
GENERATED_SPLIT_MARKER = "<!-- source:"


class ConversionDependencyMissing(RuntimeError):
    """Raised when an optional converter is needed but missing."""


class MarkItDownMissing(ConversionDependencyMissing):
    """Raised when MarkItDown is not installed. The message says what to do."""


class LiteParseMissing(ConversionDependencyMissing):
    """Raised when LiteParse is not installed. The message says what to do."""


class OptionalDependencyMissing(RuntimeError):
    """Raised when a requested optional output format needs a missing package."""


@dataclass
class ConversionOutput:
    """Text and metadata returned by a converter provider."""

    text: str
    converter: str
    converter_version: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


class ConverterProvider(Protocol):
    """Minimal interface for converter providers."""

    name: str
    supported_suffixes: set[str]

    def available(self) -> bool: ...
    def convert(self, path: Path) -> ConversionOutput: ...


@dataclass
class SourceRecord:
    """One entry in the source manifest and machine index.

    `checksum` is the short display fingerprint. `sha256` is the full content
    hash used by machines for exact matching and incremental rebuilds.
    """

    name: str
    relative_path: str
    suffix: str
    size_bytes: int
    checksum: str
    converted: bool
    note: str = ""
    sha256: str = ""
    converter: str = ""
    converter_version: str = ""
    source_kind: str = "file"
    parent_archive: str | None = None
    individual_markdown_path: str | None = None

    @property
    def status(self) -> str:
        return "included" if self.converted else (self.note or "skipped")


@dataclass
class BuildResult:
    """What a build, rebuild, add, or remove produced."""

    library_path: Path
    manifest_path: Path
    records: list[SourceRecord] = field(default_factory=list)
    individual_files: list[Path] = field(default_factory=list)
    index_path: Path | None = None
    yaml_index_path: Path | None = None

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


@dataclass
class ToolStatus:
    """One row in the `doctor` diagnostics report."""

    name: str
    available: bool
    version: str = ""
    path: str = ""
    install_command: str = ""
    note: str = ""


def _package_version(package_name: str) -> str:
    try:
        return _metadata.version(package_name)
    except _metadata.PackageNotFoundError:
        return ""


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _checksum(data: bytes) -> str:
    """Return a short fingerprint of file contents (first 12 hex characters)."""
    return _sha256_hex(data)[:12]


def _require_markitdown():
    """Load MarkItDown, or stop with a clear, friendly message."""
    try:
        from markitdown import MarkItDown  # type: ignore
    except ImportError as exc:
        raise MarkItDownMissing(
            "This needs MarkItDown to read this source file, and it is not "
            "installed yet.\n\n"
            "Command to copy:\n\n"
            "    pip install 'markitdown[all]'\n\n"
            "You can also run:\n\n"
            "    make-markdown-library setup markitdown"
        ) from exc
    return MarkItDown()


def _require_liteparse():
    """Load LiteParse, or stop with a clear, friendly message."""
    try:
        from liteparse import LiteParse  # type: ignore
    except ImportError as exc:
        raise LiteParseMissing(
            "This source was routed to LiteParse, but LiteParse is not installed.\n\n"
            "Command to copy:\n\n"
            "    pip install liteparse\n\n"
            "You can also run:\n\n"
            "    make-markdown-library setup liteparse\n\n"
            "Or rerun with --converter markitdown to use MarkItDown instead."
        ) from exc
    return LiteParse


class DirectTextConverter:
    """Read already-textual files directly without an external converter."""

    name = "direct"
    supported_suffixes = MARKDOWN_SUFFIXES | DIRECT_TEXT_SUFFIXES

    def available(self) -> bool:
        return True

    def convert(self, path: Path) -> ConversionOutput:
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("utf-8", errors="replace")
        return ConversionOutput(text=text, converter=self.name, converter_version="built-in")


class MarkItDownConverter:
    """Adapter around Microsoft MarkItDown."""

    name = "markitdown"
    supported_suffixes = MARKITDOWN_SUFFIXES

    def __init__(self) -> None:
        self._instance = None

    def available(self) -> bool:
        try:
            import markitdown  # noqa: F401
            return True
        except ImportError:
            return False

    def convert(self, path: Path) -> ConversionOutput:
        if self._instance is None:
            self._instance = _require_markitdown()
        result = self._instance.convert(str(path))
        text = getattr(result, "text_content", "") or ""
        return ConversionOutput(
            text=text,
            converter=self.name,
            converter_version=_package_version("markitdown"),
        )


class LiteParseConverter:
    """Adapter around LiteParse's Python API, configured for Markdown output."""

    name = "liteparse"
    supported_suffixes = LITEPARSE_SUFFIXES

    def __init__(self) -> None:
        self._parser = None

    def available(self) -> bool:
        try:
            import liteparse  # noqa: F401
            return True
        except ImportError:
            return False

    def convert(self, path: Path) -> ConversionOutput:
        if self._parser is None:
            LiteParse = _require_liteparse()
            self._parser = LiteParse(
                output_format="markdown",
                image_mode="placeholder",
                extract_links=True,
                quiet=True,
            )
        result = self._parser.parse(str(path))
        text = getattr(result, "text", "") or ""
        metadata: dict[str, object] = {}
        pages = getattr(result, "pages", None)
        if pages is not None:
            try:
                metadata["page_count"] = len(pages)
            except TypeError:
                pass
        return ConversionOutput(
            text=text,
            converter=self.name,
            converter_version=_package_version("liteparse"),
            metadata=metadata,
        )


class ConverterRegistry:
    """Small reusable converter cache for one build."""

    def __init__(self, mode: ConverterMode = DEFAULT_CONVERTER_MODE) -> None:
        self.mode = mode
        self.direct = DirectTextConverter()
        self.markitdown = MarkItDownConverter()
        self.liteparse = LiteParseConverter()

    def candidates(self, suffix: str) -> list[ConverterProvider]:
        """Return converters to try, in order, for this suffix.

        In auto/hybrid mode, MarkItDown is tried first for broad compatibility.
        If it returns no readable text, the build can fall back to LiteParse for
        suffixes LiteParse supports. This is especially useful for PDFs where a
        normal text extractor may return an empty document but layout/OCR-aware
        parsing can still recover useful Markdown.
        """
        suffix = suffix.lower()
        if suffix in DIRECT_TEXT_SUFFIXES:
            return [self.direct]
        if self.mode == "markitdown":
            return [self.markitdown] if suffix in self.markitdown.supported_suffixes else []
        if self.mode == "liteparse":
            return [self.liteparse] if suffix in self.liteparse.supported_suffixes else []

        providers: list[ConverterProvider] = []
        if suffix in self.markitdown.supported_suffixes:
            providers.append(self.markitdown)
        if suffix in self.liteparse.supported_suffixes:
            providers.append(self.liteparse)
        return providers

    def choose(self, suffix: str) -> ConverterProvider | None:
        """Backward-compatible helper that returns the first candidate."""
        candidates = self.candidates(suffix)
        return candidates[0] if candidates else None


def _safe_extract_zip(zip_path: Path, extract_to: Path) -> None:
    """Extract a ZIP without allowing paths to escape the target folder."""
    with zipfile.ZipFile(zip_path) as zf:
        root = extract_to.resolve()
        for member in zf.infolist():
            target = (extract_to / member.filename).resolve()
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise zipfile.BadZipFile("ZIP contains an unsafe file path") from exc
        zf.extractall(extract_to)


def _is_under(path: Path, maybe_parent: Path) -> bool:
    try:
        path.resolve().relative_to(maybe_parent.resolve())
        return True
    except ValueError:
        return False


def _is_excluded(path: Path, excluded_paths: set[Path]) -> bool:
    resolved = path.resolve()
    for excluded in excluded_paths:
        if resolved == excluded.resolve() or _is_under(resolved, excluded):
            return True
    return False


def _gather_files(
    source_path: Path,
    work_dir: Path,
    *,
    excluded_paths: set[Path] | None = None,
) -> tuple[list[Path], list[Path]]:
    """Find every usable file, unpacking ZIP files along the way.

    The input can be a single file, a folder, or a ZIP file. Nested ZIPs are
    handled. Returns (found_files, bad_zips) so the caller can report ZIPs that
    could not be opened.
    """
    found: list[Path] = []
    bad_zips: list[Path] = []
    excluded_paths = excluded_paths or set()

    def handle_file(item: Path) -> None:
        if _is_excluded(item, excluded_paths):
            return
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


def _looks_like_generated_manifest(path: Path, text: str) -> bool:
    name = path.name.lower()
    if name.endswith("-manifest.md"):
        return True
    if text.lstrip().startswith("# Markdown Library Manifest"):
        return True
    return False


def _looks_like_generated_split(text: str) -> bool:
    return text.lstrip().startswith(GENERATED_SPLIT_MARKER)


def _looks_like_index_file(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith(".index.json") or name.endswith(".index.yaml") or name.endswith(".index.yml")


def _record_from_imported_section(section: dict[str, object], library_path: Path, source_path: Path) -> SourceRecord:
    """Create a source record for a section imported from another library."""
    file_name = str(section["file"])
    converter_raw = str(section.get("converter", "imported") or "imported")
    converter, version = _split_converter_header(converter_raw)
    return SourceRecord(
        name=Path(file_name).name,
        relative_path=file_name,
        suffix=Path(file_name).suffix.lower(),
        size_bytes=0,
        checksum=str(section.get("fingerprint", "") or ""),
        sha256=str(section.get("sha256", "") or ""),
        converted=True,
        converter=converter,
        converter_version=version,
        source_kind="imported-library-section",
        note=f"imported from Markdown library: {_relative_to_source(library_path, source_path)}",
    )


def _split_converter_header(raw: str) -> tuple[str, str]:
    raw = raw.strip()
    if not raw:
        return "", ""
    if " " not in raw:
        return raw, ""
    name, version = raw.split(" ", 1)
    return name.strip(), version.strip()


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
    converter_mode: ConverterMode = DEFAULT_CONVERTER_MODE,
    markdown_policy: MarkdownPolicy = DEFAULT_MARKDOWN_POLICY,
    include_generated: bool = False,
    excluded_paths: set[Path] | None = None,
    reuse_sections_by_sha: dict[str, str] | None = None,
    reuse_metadata_by_sha: dict[str, dict[str, object]] | None = None,
) -> tuple[list[SourceRecord], list[tuple[SourceRecord, str]]]:
    """Convert source files and return records plus (record, section) pairs."""
    registry = ConverterRegistry(converter_mode)
    reuse_sections_by_sha = reuse_sections_by_sha or {}
    reuse_metadata_by_sha = reuse_metadata_by_sha or {}

    with tempfile.TemporaryDirectory() as tmp:
        work_dir = Path(tmp)
        files, bad_zips = _gather_files(source_path, work_dir, excluded_paths=excluded_paths)

        records: list[SourceRecord] = []
        section_pairs: list[tuple[SourceRecord, str]] = []

        for path in files:
            suffix = path.suffix.lower()
            data = path.read_bytes()
            full_hash = _sha256_hex(data)
            short_hash = full_hash[:12]
            relative_path = _relative_to_source(path, source_path)

            record = SourceRecord(
                name=path.name,
                relative_path=relative_path,
                suffix=suffix,
                size_bytes=len(data),
                checksum=short_hash,
                sha256=full_hash,
                converted=False,
                source_kind="file",
            )

            if _looks_like_index_file(path) and not include_generated:
                record.note = "skipped: generated index file"
                records.append(record)
                continue

            if suffix in MARKDOWN_SUFFIXES:
                markdown_output = _handle_markdown_source(
                    path,
                    data,
                    record,
                    source_path,
                    markdown_policy=markdown_policy,
                    include_generated=include_generated,
                )
                records.extend(markdown_output[0])
                section_pairs.extend(markdown_output[1])
                continue

            if not include_generated and path.parent.name.endswith("-files"):
                record.note = "skipped: generated individual Markdown output folder"
                records.append(record)
                continue

            if full_hash in reuse_sections_by_sha:
                prior = reuse_metadata_by_sha.get(full_hash, {})
                body = _section_body(reuse_sections_by_sha[full_hash])
                record.converted = True
                record.note = "reused unchanged from existing library"
                record.converter = str(prior.get("converter", "reused") or "reused")
                record.converter_version = str(prior.get("converter_version", "") or "")
                records.append(record)
                section_pairs.append((record, _format_section(record, body)))
                continue

            providers = registry.candidates(suffix)
            if not providers or suffix not in SUPPORTED_SUFFIXES:
                record.note = "skipped: file type not supported"
                records.append(record)
                continue

            attempt_notes: list[str] = []
            converted_text = ""
            conversion_result: ConversionOutput | None = None
            for provider in providers:
                try:
                    result = provider.convert(path)
                    text = (result.text or "").strip()
                except ConversionDependencyMissing as exc:
                    if converter_mode in {"markitdown", "liteparse"}:
                        raise
                    attempt_notes.append(f"{provider.name} unavailable: {exc.__class__.__name__}")
                    continue
                except Exception as exc:  # noqa: BLE001 - report, do not crash
                    attempt_notes.append(f"{provider.name} failed: {exc}")
                    continue

                if text:
                    converted_text = text
                    conversion_result = result
                    break

                attempt_notes.append(f"{provider.name} produced no readable text")

            if conversion_result is None:
                if attempt_notes:
                    record.note = "skipped: no readable text found (" + "; ".join(attempt_notes) + ")"
                else:
                    record.note = "skipped: no readable text found"
                records.append(record)
                continue

            record.converted = True
            record.converter = conversion_result.converter
            record.converter_version = conversion_result.converter_version or ""
            if attempt_notes:
                record.note = "converted after fallback: " + "; ".join(attempt_notes)
            records.append(record)
            section_pairs.append((record, _format_section(record, converted_text)))

        for bad in bad_zips:
            records.append(SourceRecord(
                name=bad.name,
                relative_path=_relative_to_source(bad, source_path),
                suffix=".zip",
                size_bytes=bad.stat().st_size if bad.exists() else 0,
                checksum="",
                sha256="",
                converted=False,
                note="skipped: ZIP could not be opened",
            ))

    section_pairs = _dedupe_section_pairs(
        section_pairs,
        existing_fingerprints=existing_fingerprints,
        allow_duplicates=allow_duplicates,
    )
    return records, section_pairs


def _handle_markdown_source(
    path: Path,
    data: bytes,
    record: SourceRecord,
    source_path: Path,
    *,
    markdown_policy: MarkdownPolicy,
    include_generated: bool,
) -> tuple[list[SourceRecord], list[tuple[SourceRecord, str]]]:
    """Handle Markdown without sending it through external converters."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="replace")

    if not include_generated and _looks_like_generated_manifest(path, text):
        record.note = "skipped: generated manifest file"
        return [record], []
    if not include_generated and _looks_like_generated_split(text):
        record.note = "skipped: generated individual Markdown file"
        return [record], []

    is_library = _is_markdown_library_text(text)
    if markdown_policy == "skip":
        record.note = "skipped: Markdown policy is skip"
        return [record], []

    if is_library:
        if markdown_policy in {"include", "import-libs"}:
            imported_sections = _parse_library_sections(text)
            if imported_sections:
                records: list[SourceRecord] = []
                pairs: list[tuple[SourceRecord, str]] = []
                for section in imported_sections:
                    imported = _record_from_imported_section(section, path, source_path)
                    records.append(imported)
                    pairs.append((imported, str(section["raw"])))
                return records, pairs
        record.note = "skipped: Markdown library had no importable source sections"
        return [record], []

    if markdown_policy == "import-libs":
        record.note = "skipped: Markdown policy only imports existing libraries"
        return [record], []

    body = text.strip()
    if not body:
        record.note = "skipped: no readable text found"
        return [record], []

    record.converted = True
    record.converter = "direct"
    record.converter_version = "built-in"
    record.source_kind = "markdown"
    return [record], [(record, _format_section(record, body))]


def _section_body(section: str) -> str:
    """Pull the converted body text back out of a formatted source section."""
    sections = _parse_library_sections(section)
    if sections:
        return _strip_markers(str(sections[0]["raw"]))
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
        header = (
            f"<!-- source: {record.relative_path} | fingerprint: {record.checksum}"
            f" | sha256: {record.sha256} -->\n\n"
        )
        out.write_text(header + body + "\n", encoding="utf-8")
        record.individual_markdown_path = str(out)
        written.append(out)
    return written


def _default_index_paths(output_path: Path, index_format: IndexFormat) -> tuple[Path | None, Path | None]:
    json_path = output_path.with_suffix(".index.json") if index_format in {"json", "both"} else None
    yaml_path = output_path.with_suffix(".index.yaml") if index_format in {"yaml", "both"} else None
    return json_path, yaml_path


def build_library(
    source_path: str | Path,
    output_path: str | Path | None = None,
    purpose: str = "",
    *,
    title: str = "Markdown Library File",
    allow_duplicates: bool = False,
    individual_files: bool | str | Path = False,
    converter_mode: ConverterMode = DEFAULT_CONVERTER_MODE,
    markdown_policy: MarkdownPolicy = DEFAULT_MARKDOWN_POLICY,
    include_generated: bool = False,
    index_format: IndexFormat = DEFAULT_INDEX_FORMAT,
    index_path: str | Path | None = None,
    reuse_sections_by_sha: dict[str, str] | None = None,
    reuse_metadata_by_sha: dict[str, dict[str, object]] | None = None,
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
        converter_mode: markitdown, liteparse, auto, or hybrid.
        markdown_policy: include normal Markdown, import only existing
            libraries, or skip Markdown files.
        include_generated: include generated manifests/indexes/split files.
        index_format: json, yaml, both, or none.
    """
    source_path = Path(source_path).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source_path}")

    if output_path is None:
        parent = source_path.parent if source_path.is_file() else source_path.parent
        output_path = parent / DEFAULT_LIBRARY_NAME
    output_path = Path(output_path).expanduser().resolve()
    manifest_path = output_path.with_name(output_path.stem + "-manifest.md")

    if index_path is not None and index_format in {"json", "both"}:
        json_index_path: Path | None = Path(index_path).expanduser().resolve()
        yaml_index_path: Path | None = output_path.with_suffix(".index.yaml") if index_format == "both" else None
    else:
        json_index_path, yaml_index_path = _default_index_paths(output_path, index_format)

    default_split_dir = output_path.with_name(output_path.stem + "-files")
    excluded_paths = {output_path, manifest_path}
    if json_index_path:
        excluded_paths.add(json_index_path)
    if yaml_index_path:
        excluded_paths.add(yaml_index_path)
    if not include_generated:
        excluded_paths.add(default_split_dir)

    records, section_pairs = _convert_sources(
        source_path,
        allow_duplicates=allow_duplicates,
        converter_mode=converter_mode,
        markdown_policy=markdown_policy,
        include_generated=include_generated,
        excluded_paths=excluded_paths,
        reuse_sections_by_sha=reuse_sections_by_sha,
        reuse_metadata_by_sha=reuse_metadata_by_sha,
    )
    sections = [section for _, section in section_pairs]

    _write_library(output_path, purpose, source_path, records, sections, title, converter_mode, markdown_policy)
    _write_manifest(manifest_path, purpose, source_path, records)

    written: list[Path] = []
    if individual_files:
        if individual_files is True:
            target_dir = default_split_dir
        else:
            target_dir = Path(individual_files).expanduser().resolve()
        written = _write_individual_files(section_pairs, target_dir)

    if index_format != "none":
        _write_index_files(
            library_path=output_path,
            json_index_path=json_index_path,
            yaml_index_path=yaml_index_path,
            purpose=purpose,
            title=title,
            source_path=source_path,
            records=records,
            settings={
                "converter_mode": converter_mode,
                "markdown_policy": markdown_policy,
                "allow_duplicates": allow_duplicates,
                "individual_files": bool(individual_files),
                "include_generated": include_generated,
            },
        )

    return BuildResult(
        library_path=output_path,
        manifest_path=manifest_path,
        records=records,
        individual_files=written,
        index_path=json_index_path,
        yaml_index_path=yaml_index_path,
    )


def rebuild_library(
    index_file: str | Path,
    *,
    output_path: str | Path | None = None,
    converter_mode: ConverterMode | None = None,
    markdown_policy: MarkdownPolicy | None = None,
    index_format: IndexFormat | None = None,
) -> BuildResult:
    """Rebuild a library from a previous JSON index, reusing unchanged sections.

    The index stores full SHA-256 hashes. If a current source file has the same
    hash as a previous source and the old library is still available, that
    section is reused without running a converter again.
    """
    index_file = Path(index_file).expanduser().resolve()
    if not index_file.is_file():
        raise FileNotFoundError(f"Index file not found: {index_file}")
    index = json.loads(index_file.read_text(encoding="utf-8"))

    library_info = index.get("library", {})
    source_input = library_info.get("source_input_path") or library_info.get("source_input")
    if not source_input:
        raise ValueError("Index file does not record a source_input_path.")
    source_path = Path(str(source_input)).expanduser().resolve()
    old_library_path = Path(str(library_info.get("path", ""))).expanduser().resolve()
    target_library_path = Path(output_path).expanduser().resolve() if output_path else old_library_path

    settings = index.get("settings", {})
    mode = converter_mode or settings.get("converter_mode", DEFAULT_CONVERTER_MODE)
    md_policy = markdown_policy or settings.get("markdown_policy", DEFAULT_MARKDOWN_POLICY)
    fmt = index_format or DEFAULT_INDEX_FORMAT
    individual = bool(settings.get("individual_files", False))
    include_generated = bool(settings.get("include_generated", False))
    allow_duplicates = bool(settings.get("allow_duplicates", False))

    reuse_sections_by_sha: dict[str, str] = {}
    reuse_metadata_by_sha: dict[str, dict[str, object]] = {}
    if old_library_path.is_file():
        old_text = old_library_path.read_text(encoding="utf-8")
        for section in _parse_library_sections(old_text):
            sha = str(section.get("sha256", "") or "")
            if sha:
                reuse_sections_by_sha[sha] = str(section["raw"])

    for source in index.get("sources", []):
        if not isinstance(source, dict):
            continue
        sha = str(source.get("sha256", "") or "")
        if sha:
            reuse_metadata_by_sha[sha] = source

    return build_library(
        source_path,
        target_library_path,
        purpose=str(library_info.get("purpose", "") or ""),
        title=str(library_info.get("title", "Markdown Library File") or "Markdown Library File"),
        allow_duplicates=allow_duplicates,
        individual_files=individual,
        converter_mode=mode,  # type: ignore[arg-type]
        markdown_policy=md_policy,  # type: ignore[arg-type]
        include_generated=include_generated,
        index_format=fmt,
        reuse_sections_by_sha=reuse_sections_by_sha,
        reuse_metadata_by_sha=reuse_metadata_by_sha,
    )


def add_to_library(
    library_path: str | Path,
    source_path: str | Path,
    purpose: str = "",
    *,
    skip_duplicates: bool = True,
    converter_mode: ConverterMode = DEFAULT_CONVERTER_MODE,
    markdown_policy: MarkdownPolicy = DEFAULT_MARKDOWN_POLICY,
    include_generated: bool = False,
    index_format: IndexFormat = DEFAULT_INDEX_FORMAT,
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
    existing_fingerprints = {str(sec.get("fingerprint", "") or "") for sec in existing_sections}
    manifest_path = library_path.with_name(library_path.stem + "-manifest.md")
    json_index_path, yaml_index_path = _default_index_paths(library_path, index_format)

    records, section_pairs = _convert_sources(
        source_path,
        existing_fingerprints=existing_fingerprints,
        allow_duplicates=not skip_duplicates,
        converter_mode=converter_mode,
        markdown_policy=markdown_policy,
        include_generated=include_generated,
        excluded_paths={library_path, manifest_path, *(p for p in [json_index_path, yaml_index_path] if p)},
    )
    sections_to_add = [section for _, section in section_pairs]

    if sections_to_add:
        new_sections: list[dict[str, object]] = []
        for section in sections_to_add:
            new_sections.extend(_parse_library_sections(section))
        all_sections = existing_sections + new_sections
        _write_library_from_sections(library_path, all_sections)
        _write_manifest_from_sections(manifest_path, all_sections)
    else:
        all_sections = existing_sections

    if index_format != "none":
        index_records = _records_from_sections(all_sections)
        _write_index_files(
            library_path=library_path,
            json_index_path=json_index_path,
            yaml_index_path=yaml_index_path,
            purpose=purpose,
            title="Markdown Library File",
            source_path=source_path,
            records=index_records + [r for r in records if not r.converted],
            settings={
                "converter_mode": converter_mode,
                "markdown_policy": markdown_policy,
                "allow_duplicates": not skip_duplicates,
                "individual_files": False,
                "include_generated": include_generated,
            },
        )

    return BuildResult(
        library_path=library_path,
        manifest_path=manifest_path,
        records=records,
        index_path=json_index_path,
        yaml_index_path=yaml_index_path,
    )


def list_library_sources(library_path: str | Path) -> list[str]:
    """Return the source names recorded in a Markdown library file."""
    library_path = Path(library_path).expanduser().resolve()
    if not library_path.is_file():
        raise FileNotFoundError(f"Markdown library file not found: {library_path}")
    text = library_path.read_text(encoding="utf-8")
    return [str(section["file"]) for section in _parse_library_sections(text)]


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


def remove_file_from_library(library_path: str | Path, selector: str | int, *, index_format: IndexFormat = DEFAULT_INDEX_FORMAT) -> BuildResult:
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
        matches = [i for i, sec in enumerate(sections) if sec["file"] == selector_text or Path(str(sec["file"])).name == selector_text]
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

    json_index_path, yaml_index_path = _default_index_paths(library_path, index_format)
    if index_format != "none":
        _write_index_files(
            library_path=library_path,
            json_index_path=json_index_path,
            yaml_index_path=yaml_index_path,
            purpose="",
            title="Markdown Library File",
            source_path=library_path.parent,
            records=_records_from_sections(sections),
            settings={"operation": "remove-file"},
        )

    record = SourceRecord(
        name=Path(str(removed["file"])).name,
        relative_path=str(removed["file"]),
        suffix=Path(str(removed["file"])).suffix.lower(),
        size_bytes=0,
        checksum=str(removed.get("fingerprint", "") or ""),
        sha256=str(removed.get("sha256", "") or ""),
        converted=True,
        note="removed",
    )
    return BuildResult(
        library_path=library_path,
        manifest_path=manifest_path,
        records=[record],
        index_path=json_index_path,
        yaml_index_path=yaml_index_path,
    )


def _format_section(record: SourceRecord, text: str) -> str:
    """Wrap one converted source in clear start and end markers."""
    converter = record.converter or "unknown"
    if record.converter_version:
        converter = f"{converter} {record.converter_version}"
    header = (
        f"{DELIMITER}\n"
        f"SOURCE START\n"
        f"File: {record.relative_path}\n"
        f"Fingerprint: {record.checksum}\n"
        f"SHA256: {record.sha256}\n"
        f"Converter: {converter}\n"
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
    converter_mode: str,
    markdown_policy: str,
) -> None:
    today = _dt.date.today().isoformat()
    converted = [r for r in records if r.converted]
    lines = [
        LIBRARY_METADATA_MARKER,
        f"# {title}",
        "",
        "This file was built by Make Markdown Library from your source files.",
        "Each source below is wrapped in START and END markers so an AI can tell the sources apart.",
        "",
        f"- Built on: {today}",
        f"- Source input: {source_path.name}",
        f"- Sources included: {len(converted)}",
        f"- Sources skipped: {len(records) - len(converted)}",
        f"- Converter mode: {converter_mode}",
        f"- Markdown policy: {markdown_policy}",
    ]
    if purpose:
        lines += ["", f"**Purpose:** {purpose}"]
    lines += ["", "## Source manifest", "", _manifest_table_header()]
    for i, r in enumerate(converted, start=1):
        lines.append(_manifest_row(r, i))
    lines += ["", "---", ""]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n" + "\n".join(sections), encoding="utf-8")


def _write_library_from_sections(output_path: Path, sections: list[dict[str, object]]) -> None:
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
    for i, record in enumerate(_records_from_sections(sections), start=1):
        lines.append(_manifest_row(record, i))
    lines += ["", "---", ""]
    output_path.write_text("\n".join(lines) + "\n" + "\n".join(str(sec["raw"]).rstrip() for sec in sections) + "\n", encoding="utf-8")


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
    sections: list[dict[str, object]],
) -> None:
    """Write a manifest from the source sections currently in a library file."""
    lines = [
        "# Markdown Library Manifest",
        "",
        "This manifest was regenerated from the current Markdown library file.",
        "",
        _manifest_table_header(),
    ]
    for i, record in enumerate(_records_from_sections(sections), start=1):
        lines.append(_manifest_row(record, i))
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _manifest_table_header() -> str:
    return "| No. | File | Type | Size (bytes) | Fingerprint | Converter | Status |\n| ---: | --- | --- | ---: | --- | --- | --- |"


def _manifest_row(record: SourceRecord, number: int) -> str:
    size = record.size_bytes if record.size_bytes else ""
    converter = record.converter or ""
    if record.converter_version:
        converter = f"{converter} {record.converter_version}".strip()
    return (
        f"| {number} | {record.relative_path} | {record.suffix or ''} | "
        f"{size} | {record.checksum} | {converter} | {record.status} |"
    )


def _records_from_sections(sections: list[dict[str, object]]) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for sec in sections:
        file_name = str(sec.get("file", ""))
        converter, version = _split_converter_header(str(sec.get("converter", "") or ""))
        records.append(SourceRecord(
            name=Path(file_name).name,
            relative_path=file_name,
            suffix=Path(file_name).suffix.lower(),
            size_bytes=0,
            checksum=str(sec.get("fingerprint", "") or ""),
            sha256=str(sec.get("sha256", "") or ""),
            converted=True,
            converter=converter,
            converter_version=version,
        ))
    return records


def _write_index_files(
    *,
    library_path: Path,
    json_index_path: Path | None,
    yaml_index_path: Path | None,
    purpose: str,
    title: str,
    source_path: Path,
    records: list[SourceRecord],
    settings: dict[str, object],
) -> None:
    index = _build_index(library_path, purpose, title, source_path, records, settings)
    if json_index_path:
        json_index_path.parent.mkdir(parents=True, exist_ok=True)
        json_index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if yaml_index_path:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise OptionalDependencyMissing(
                "YAML index output needs PyYAML. Install it with:\n\n"
                "    pip install PyYAML\n\n"
                "Or use --index-format json."
            ) from exc
        yaml_index_path.parent.mkdir(parents=True, exist_ok=True)
        yaml_index_path.write_text(yaml.safe_dump(index, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _build_index(
    library_path: Path,
    purpose: str,
    title: str,
    source_path: Path,
    records: list[SourceRecord],
    settings: dict[str, object],
) -> dict[str, object]:
    text = library_path.read_text(encoding="utf-8") if library_path.is_file() else ""
    positions = _section_positions(text)
    used_positions: set[int] = set()

    sources: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    for i, record in enumerate(records, start=1):
        item: dict[str, object] = {
            "id": f"src_{i:04d}",
            "status": "included" if record.converted else "skipped",
            "name": record.name,
            "relative_path": record.relative_path,
            "suffix": record.suffix,
            "size_bytes": record.size_bytes,
            "sha256": record.sha256,
            "fingerprint": record.checksum,
            "converter": record.converter,
            "converter_version": record.converter_version,
            "source_kind": record.source_kind,
            "parent_archive": record.parent_archive,
            "individual_markdown_path": record.individual_markdown_path,
            "notes": [record.note] if record.note else [],
        }
        if record.converted:
            pos_index, pos = _find_position_for_record(record, positions, used_positions)
            if pos:
                used_positions.add(pos_index)
                item["library_section"] = pos
            sources.append(item)
        else:
            skipped.append({
                "relative_path": record.relative_path,
                "reason": record.note or "skipped",
                "suffix": record.suffix,
                "fingerprint": record.checksum,
            })
            sources.append(item)

    return {
        "schema_version": "1.0",
        "tool": {
            "name": "make-markdown-library",
            "version": _package_version("make-markdown-library"),
        },
        "library": {
            "path": str(library_path),
            "title": title,
            "built_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "source_input": source_path.name,
            "source_input_path": str(source_path),
            "purpose": purpose,
        },
        "settings": settings,
        "sources": sources,
        "skipped": skipped,
    }


def _find_position_for_record(
    record: SourceRecord,
    positions: list[dict[str, object]],
    used_positions: set[int],
) -> tuple[int, dict[str, int] | None]:
    for i, pos in enumerate(positions):
        if i in used_positions:
            continue
        if pos.get("file") == record.relative_path and pos.get("fingerprint") == record.checksum:
            return i, pos.get("library_section")  # type: ignore[return-value]
    return -1, None


def _section_positions(text: str) -> list[dict[str, object]]:
    positions: list[dict[str, object]] = []
    for match in _SECTION_PATTERN.finditer(text):
        start_char, end_char = match.span()
        start_line = text.count("\n", 0, start_char) + 1
        end_line = text.count("\n", 0, end_char) + 1
        positions.append({
            "file": match.group("file").strip(),
            "fingerprint": match.group("fingerprint").strip(),
            "library_section": {
                "start_line": start_line,
                "end_line": end_line,
                "start_char": start_char,
                "end_char": end_char,
            },
        })
    return positions


_SECTION_PATTERN = re.compile(
    rf"{re.escape(DELIMITER)}\n"
    rf"SOURCE START\n"
    rf"File: (?P<file>.*?)\n"
    rf"Fingerprint: (?P<fingerprint>.*?)\n"
    rf"(?:SHA256: (?P<sha256>.*?)\n)?"
    rf"(?:Converter: (?P<converter>.*?)\n)?"
    rf"{re.escape(DELIMITER)}\n"
    rf"(?P<body>.*?)\n"
    rf"{re.escape(DELIMITER)}\n"
    rf"SOURCE END: .*?\n"
    rf"{re.escape(DELIMITER)}",
    flags=re.DOTALL,
)


def _parse_library_sections(text: str) -> list[dict[str, object]]:
    """Return source sections from a Markdown library file."""
    sections: list[dict[str, object]] = []
    for match in _SECTION_PATTERN.finditer(text):
        sections.append({
            "file": match.group("file").strip(),
            "fingerprint": match.group("fingerprint").strip(),
            "sha256": (match.group("sha256") or "").strip(),
            "converter": (match.group("converter") or "").strip(),
            "raw": match.group(0),
        })
    return sections


def diagnose_environment() -> list[ToolStatus]:
    """Return diagnostics for Python, converters, and optional system tools."""
    statuses: list[ToolStatus] = []
    statuses.append(ToolStatus(
        name="python",
        available=True,
        version=sys.version.split()[0],
        path=sys.executable,
    ))

    for package_name, label, command in [
        ("markitdown", "MarkItDown", "pip install 'markitdown[all]'"),
        ("liteparse", "LiteParse", "pip install liteparse"),
        ("yaml", "PyYAML", "pip install PyYAML"),
    ]:
        if package_name == "yaml":
            available = _module_available("yaml")
            version = _package_version("PyYAML") if available else ""
        else:
            available = _module_available(package_name)
            version = _package_version(package_name) if available else ""
        statuses.append(ToolStatus(
            name=label,
            available=available,
            version=version,
            install_command=command,
        ))

    statuses.append(ToolStatus(
        name="lit CLI",
        available=shutil.which("lit") is not None,
        path=shutil.which("lit") or "",
        install_command="pip install liteparse",
        note="Installed with LiteParse; useful for manual parsing and debugging.",
    ))
    statuses.append(ToolStatus(
        name="LibreOffice",
        available=shutil.which("soffice") is not None or shutil.which("libreoffice") is not None,
        path=shutil.which("soffice") or shutil.which("libreoffice") or "",
        note="Optional: improves LiteParse coverage for Office/OpenDocument formats.",
    ))
    statuses.append(ToolStatus(
        name="ImageMagick",
        available=shutil.which("magick") is not None or shutil.which("convert") is not None,
        path=shutil.which("magick") or shutil.which("convert") or "",
        note="Optional: improves LiteParse coverage for image inputs.",
    ))
    statuses.append(ToolStatus(
        name="Tkinter",
        available=_module_available("tkinter"),
        note="Needed only for the GUI.",
    ))
    return statuses


def _module_available(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def install_optional_tool(tool: str, *, yes: bool = False) -> int:
    """Install an optional tool using the current Python interpreter's pip."""
    normalized = tool.lower().strip()
    packages = {
        "markitdown": ["markitdown[all]"],
        "liteparse": ["liteparse"],
        "yaml": ["PyYAML"],
        "pyyaml": ["PyYAML"],
        "all-converters": ["markitdown[all]", "liteparse", "PyYAML"],
    }.get(normalized)
    if not packages:
        raise ValueError("Tool must be one of: markitdown, liteparse, yaml, all-converters")

    command = [sys.executable, "-m", "pip", "install", *packages]
    if not yes:
        print("This will run:")
        print("  " + " ".join(command))
        answer = input("Install now? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Cancelled.")
            return 1
    completed = subprocess.run(command, check=False)
    return completed.returncode
