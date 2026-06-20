"""Tests for the Make Markdown Library engine.

These tests mock MarkItDown so they run anywhere. They cover the parts that are
ours: gathering files, dedup, ZIP safety, the library/manifest format, the
split-files feature, and remove/list/check.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from make_markdown_library import core


class FakeResult:
    def __init__(self, text: str) -> None:
        self.text_content = text


class FakeMarkItDown:
    """Stand-in for MarkItDown: returns the file's text, uppercased per name."""

    def convert(self, path: str) -> FakeResult:
        p = Path(path)
        return FakeResult(f"Converted body of {p.name}")


@pytest.fixture(autouse=True)
def _patch_markitdown(monkeypatch):
    monkeypatch.setattr(core, "_require_markitdown", lambda: FakeMarkItDown())


def _make_sources(tmp_path: Path) -> Path:
    src = tmp_path / "sources"
    src.mkdir()
    (src / "a.txt").write_text("alpha", encoding="utf-8")
    (src / "b.docx").write_bytes(b"fake docx bytes")
    (src / "notes.md").write_text("# Plain markdown note", encoding="utf-8")
    return src


def test_build_library_creates_library_and_manifest(tmp_path):
    src = _make_sources(tmp_path)
    out = tmp_path / "markdown-library.md"
    result = core.build_library(src, out)

    assert result.library_path.is_file()
    assert result.manifest_path.is_file()
    assert result.converted_count == 3
    text = result.library_path.read_text(encoding="utf-8")
    assert core.LIBRARY_METADATA_MARKER in text
    assert text.count("SOURCE START") == 3
    assert "Converted body of a.txt" in text


def test_default_library_name(tmp_path):
    src = _make_sources(tmp_path)
    result = core.build_library(src)
    assert result.library_path.name == core.DEFAULT_LIBRARY_NAME


def test_individual_files_true_writes_one_per_source(tmp_path):
    src = _make_sources(tmp_path)
    out = tmp_path / "markdown-library.md"
    result = core.build_library(src, out, individual_files=True)

    assert len(result.individual_files) == 3
    target = out.with_name(out.stem + "-files")
    assert target.is_dir()
    names = sorted(p.name for p in result.individual_files)
    assert names == ["a.md", "b.md", "notes.md"]
    body = (target / "a.md").read_text(encoding="utf-8")
    assert "source: a.txt" in body
    assert "Converted body of a.txt" in body


def test_individual_files_custom_dir(tmp_path):
    src = _make_sources(tmp_path)
    out = tmp_path / "markdown-library.md"
    split_dir = tmp_path / "split-out"
    result = core.build_library(src, out, individual_files=split_dir)
    assert all(p.parent == split_dir for p in result.individual_files)


def test_duplicates_skipped_by_default(tmp_path):
    src = tmp_path / "sources"
    src.mkdir()
    (src / "one.txt").write_text("same content", encoding="utf-8")
    (src / "two.txt").write_text("same content", encoding="utf-8")
    out = tmp_path / "lib.md"
    result = core.build_library(src, out)
    assert result.converted_count == 1
    assert result.skipped_count == 1
    assert any("duplicate" in r.note for r in result.records)


def test_allow_duplicates_keeps_both(tmp_path):
    src = tmp_path / "sources"
    src.mkdir()
    (src / "one.txt").write_text("same content", encoding="utf-8")
    (src / "two.txt").write_text("same content", encoding="utf-8")
    out = tmp_path / "lib.md"
    result = core.build_library(src, out, allow_duplicates=True)
    assert result.converted_count == 2


def test_unsupported_type_is_skipped(tmp_path):
    src = tmp_path / "sources"
    src.mkdir()
    (src / "image.xyz").write_bytes(b"not supported")
    out = tmp_path / "lib.md"
    result = core.build_library(src, out)
    assert result.converted_count == 0
    assert any("not supported" in r.note for r in result.records)


def test_zip_is_unpacked(tmp_path):
    src = tmp_path / "sources"
    src.mkdir()
    zip_path = src / "bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("inside.txt", "zipped content")
    out = tmp_path / "lib.md"
    result = core.build_library(src, out)
    assert result.converted_count == 1
    assert any("inside.txt" in r.relative_path for r in result.records if r.converted)


def test_bad_zip_is_reported_not_fatal(tmp_path):
    src = tmp_path / "sources"
    src.mkdir()
    (src / "broken.zip").write_bytes(b"this is not a zip")
    (src / "ok.txt").write_text("fine", encoding="utf-8")
    out = tmp_path / "lib.md"
    result = core.build_library(src, out)
    assert result.converted_count == 1
    assert any("ZIP could not be opened" in r.note for r in result.records)


def test_zip_slip_is_blocked(tmp_path):
    src = tmp_path / "sources"
    src.mkdir()
    zip_path = src / "evil.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("../escaped.txt", "should not escape")
    out = tmp_path / "lib.md"
    result = core.build_library(src, out)
    # The unsafe ZIP is treated as a bad ZIP and reported, not extracted.
    assert any("ZIP could not be opened" in r.note for r in result.records)
    assert not (tmp_path / "escaped.txt").exists()


def test_list_and_remove_and_check(tmp_path):
    src = _make_sources(tmp_path)
    out = tmp_path / "lib.md"
    core.build_library(src, out)

    sources = core.list_library_sources(out)
    assert len(sources) == 3

    report = core.check_library_format(out)
    assert report.looks_valid
    assert report.source_count == 3

    core.remove_file_from_library(out, 1)
    assert len(core.list_library_sources(out)) == 2
    assert out.with_name(out.stem + ".backup.md").is_file()


def test_add_to_library_merges_and_dedupes(tmp_path):
    src = _make_sources(tmp_path)
    out = tmp_path / "lib.md"
    core.build_library(src, out)

    more = tmp_path / "more"
    more.mkdir()
    (more / "c.txt").write_text("gamma", encoding="utf-8")
    result = core.add_to_library(out, more)
    assert result.converted_count == 1
    assert len(core.list_library_sources(out)) == 4
