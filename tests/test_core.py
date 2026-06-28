"""Tests for the Make Markdown Library engine."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from make_markdown_library import core


class FakeResult:
    def __init__(self, text: str) -> None:
        self.text_content = text


class FakeMarkItDown:
    """Stand-in for MarkItDown: returns predictable converted text."""

    def convert(self, path: str) -> FakeResult:
        p = Path(path)
        return FakeResult(f"Converted body of {p.name}")


class FakeLiteParseResult:
    text = "LiteParse markdown body"
    pages = [object(), object()]


class FakeLiteParse:
    last_kwargs: dict[str, object] = {}

    def __init__(self, **kwargs) -> None:
        FakeLiteParse.last_kwargs = kwargs

    def parse(self, _path: str) -> FakeLiteParseResult:
        return FakeLiteParseResult()


@pytest.fixture(autouse=True)
def _patch_converters(monkeypatch):
    monkeypatch.setattr(core, "_require_markitdown", lambda: FakeMarkItDown())
    monkeypatch.setattr(core.MarkItDownConverter, "available", lambda self: True)
    monkeypatch.setattr(core, "_require_liteparse", lambda: FakeLiteParse)
    monkeypatch.setattr(core.LiteParseConverter, "available", lambda self: True)
    monkeypatch.setattr(core, "_package_version", lambda package: {"markitdown": "0.test", "liteparse": "2.test"}.get(package, ""))


def _make_sources(tmp_path: Path) -> Path:
    src = tmp_path / "sources"
    src.mkdir()
    (src / "a.txt").write_text("alpha", encoding="utf-8")
    (src / "b.docx").write_bytes(b"fake docx bytes")
    (src / "notes.md").write_text("# Plain markdown note", encoding="utf-8")
    return src


def test_build_library_creates_library_manifest_and_index(tmp_path):
    src = _make_sources(tmp_path)
    out = tmp_path / "markdown-library.md"
    result = core.build_library(src, out)

    assert result.library_path.is_file()
    assert result.manifest_path.is_file()
    assert result.index_path and result.index_path.is_file()
    assert result.converted_count == 3
    text = result.library_path.read_text(encoding="utf-8")
    assert core.LIBRARY_METADATA_MARKER in text
    assert text.count("SOURCE START") == 3
    assert "alpha" in text  # .txt is read directly now
    assert "Converted body of b.docx" in text
    assert "# Plain markdown note" in text

    index = json.loads(result.index_path.read_text(encoding="utf-8"))
    assert index["schema_version"] == "1.1"
    assert len(index["sources"]) == 3
    assert all("sha256" in source for source in index["sources"])
    assert all("library_section" in source for source in index["sources"])
    assert all("output" in source for source in index["sources"])
    assert all("fallback" in source for source in index["sources"])
    assert all("complexity" in source for source in index["sources"])
    assert all("markdown" in source for source in index["sources"])


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
    assert "alpha" in body


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
    assert out.with_suffix(".index.json").is_file()


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
    assert out.with_suffix(".index.json").is_file()


def test_liteparse_converter_mode_for_pdf(tmp_path):
    src = tmp_path / "sources"
    src.mkdir()
    (src / "scan.pdf").write_bytes(b"fake pdf")
    out = tmp_path / "lib.md"

    result = core.build_library(src, out, converter_mode="liteparse")
    assert result.converted_count == 1
    text = out.read_text(encoding="utf-8")
    assert "LiteParse markdown body" in text
    assert "Converter: liteparse" in text




def test_auto_mode_falls_back_to_liteparse_when_markitdown_is_empty(tmp_path, monkeypatch):
    class EmptyMarkItDown:
        def convert(self, _path: str) -> FakeResult:
            return FakeResult("")

    monkeypatch.setattr(core, "_require_markitdown", lambda: EmptyMarkItDown())

    src = tmp_path / "sources"
    src.mkdir()
    (src / "scan.pdf").write_bytes(b"fake pdf")
    out = tmp_path / "lib.md"

    result = core.build_library(src, out, converter_mode="auto")

    assert result.converted_count == 1
    record = next(r for r in result.records if r.converted)
    assert record.converter == "liteparse"
    assert "markitdown produced no readable text" in record.note
    text = out.read_text(encoding="utf-8")
    assert "LiteParse markdown body" in text
    assert "Converter: liteparse" in text


def test_markdown_policy_import_libraries_and_skip_plain_markdown(tmp_path):
    src = _make_sources(tmp_path)
    old = tmp_path / "old.md"
    core.build_library(src, old, index_format="none")

    new_src = tmp_path / "new-src"
    new_src.mkdir()
    (new_src / "plain.md").write_text("plain should be skipped", encoding="utf-8")
    (new_src / "old.md").write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp_path / "new.md"

    result = core.build_library(new_src, out, markdown_policy="import-libs")
    assert result.converted_count == 3
    text = out.read_text(encoding="utf-8")
    assert "plain should be skipped" not in text
    assert len(core.list_library_sources(out)) == 3


def test_generated_markdown_files_are_skipped_by_default(tmp_path):
    src = _make_sources(tmp_path)
    out = tmp_path / "lib.md"
    core.build_library(src, out, individual_files=True)

    # Rebuilding from the parent folder should not ingest the previous manifest,
    # index, or split files unless include_generated=True.
    result = core.build_library(tmp_path, tmp_path / "second.md")
    assert not any("-manifest.md" in r.relative_path and r.converted for r in result.records)
    assert not any(r.relative_path.endswith(".index.json") and r.converted for r in result.records)
    assert not any("lib-files" in r.relative_path and r.converted for r in result.records)


def test_rebuild_reuses_unchanged_sections(tmp_path, monkeypatch):
    src = _make_sources(tmp_path)
    out = tmp_path / "lib.md"
    first = core.build_library(src, out)
    assert first.index_path

    def fail_markitdown():
        raise AssertionError("MarkItDown should not be needed for unchanged docx")

    monkeypatch.setattr(core, "_require_markitdown", fail_markitdown)
    result = core.rebuild_library(first.index_path)

    assert result.converted_count == 3
    assert any("reused unchanged" in r.note for r in result.records)



def test_liteparse_options_are_passed_and_recorded(tmp_path):
    src = tmp_path / "sources"
    src.mkdir()
    (src / "scan.pdf").write_bytes(b"fake pdf")
    out = tmp_path / "lib.md"

    result = core.build_library(
        src,
        out,
        converter_mode="liteparse",
        liteparse_options={
            "image_mode": "off",
            "extract_links": False,
            "ocr": False,
            "ocr_language": "fra",
            "dpi": 200,
            "max_pages": 3,
        },
    )

    assert result.converted_count == 1
    assert FakeLiteParse.last_kwargs["image_mode"] == "off"
    assert FakeLiteParse.last_kwargs["extract_links"] is False
    assert FakeLiteParse.last_kwargs["ocr"] is False
    assert FakeLiteParse.last_kwargs["ocr_language"] == "fra"
    assert FakeLiteParse.last_kwargs["dpi"] == 200
    index = json.loads(result.index_path.read_text(encoding="utf-8"))
    source = index["sources"][0]
    assert source["converter_options"]["image_mode"] == "off"
    assert source["converter_options"]["extract_links"] is False
    assert source["output"]["char_count"] > 0


def test_complex_pdf_prefers_liteparse_in_auto_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "_liteparse_complexity_check", lambda _path: {"checked": True, "complex": True, "reason": "ocr_required"})
    src = tmp_path / "sources"
    src.mkdir()
    (src / "scan.pdf").write_bytes(b"fake pdf")
    out = tmp_path / "lib.md"

    result = core.build_library(
        src,
        out,
        converter_mode="auto",
        liteparse_options={"complexity_check": True},
    )

    record = next(r for r in result.records if r.converted)
    assert record.converter == "liteparse"
    assert record.complexity_checked is True
    assert record.complexity_complex is True
    index = json.loads(result.index_path.read_text(encoding="utf-8"))
    assert index["sources"][0]["complexity"]["reason"] == "ocr_required"


def test_plan_rebuild_dry_run_counts_unchanged_files(tmp_path):
    src = _make_sources(tmp_path)
    out = tmp_path / "lib.md"
    first = core.build_library(src, out)
    plan = core.plan_rebuild(first.index_path)
    assert plan["counts"]["would_skip"] == 3
    assert plan["counts"]["would_rebuild"] == 0
