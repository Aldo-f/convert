"""Tests for text-to-text conversion (shared text_to_text module)."""

import os
from pathlib import Path

from click.testing import CliRunner

from convert.cli import cli
from convert.registry import registry

_TEXT_FORMATS = ("txt", "md", "docx")
_PAIRS = [
    ("txt", "md"),
    ("md", "txt"),
    ("txt", "docx"),
    ("docx", "txt"),
    ("md", "docx"),
    ("docx", "md"),
]


def _make_txt(tmp_path, name, content="hello world"):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def _make_md(tmp_path, name, content="# Title\n\n**bold** text"):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def _make_docx(tmp_path, name, content="hello world"):
    """Generate a minimal DOCX file using python-docx."""
    from docx import Document

    path = tmp_path / name
    doc = Document()
    for line in content.splitlines():
        doc.add_paragraph(line)
    doc.save(path)
    return path


def _read(path):
    return path.read_text(encoding="utf-8")


def test_txt_to_md(tmp_path):
    src = _make_txt(tmp_path, "in.txt", "plain text")
    out = tmp_path / "out.md"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    assert out.exists()
    assert _read(out) == "plain text"


def test_md_to_txt(tmp_path):
    src = _make_md(tmp_path, "in.md", "# Title\n\n**bold** text")
    out = tmp_path / "out.txt"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    assert out.exists()
    content = _read(out)
    assert "Title" in content
    assert "bold" in content
    assert "#" not in content
    assert "**" not in content


def test_txt_to_docx(tmp_path):
    src = _make_txt(tmp_path, "in.txt", "line1\nline2")
    out = tmp_path / "out.docx"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    assert out.exists()
    assert out.stat().st_size > 0


def test_docx_to_txt(tmp_path):
    src = _make_docx(tmp_path, "in.docx", "para1\npara2")
    out = tmp_path / "out.txt"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    assert out.exists()
    content = _read(out)
    assert "para1" in content
    assert "para2" in content


def test_md_to_docx(tmp_path):
    src = _make_md(tmp_path, "in.md", "# Heading\n\n**bold**")
    out = tmp_path / "out.docx"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    assert out.exists()
    assert out.stat().st_size > 0


def test_docx_to_md(tmp_path):
    src = _make_docx(tmp_path, "in.docx", "para1\npara2")
    out = tmp_path / "out.md"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    assert out.exists()
    content = _read(out)
    assert "para1" in content
    assert "para2" in content


def test_all_text_pairs_registered():
    for src, dst in _PAIRS:
        assert registry.get(src, dst) is not None, f"{src} -> {dst} not registered"


def test_same_format_pairs_not_registered():
    # Same-format pairs are not registered (loop skips them)
    for fmt in _TEXT_FORMATS:
        assert registry.get(fmt, fmt) is None, f"{fmt} -> {fmt} should not be registered"


def test_non_text_file_errors(tmp_path):
    src = tmp_path / "in.bin"
    src.write_bytes(b"\x00\x01\x02")
    out = tmp_path / "out.txt"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code != 0


def test_txt_to_md_preserves_content(tmp_path):
    src = _make_txt(tmp_path, "in.txt", "line1\nline2\nline3")
    out = tmp_path / "out.md"
    r = CliRunner().invoke(cli, ["convert", str(src), str(out)])
    assert r.exit_code == 0
    assert _read(out) == "line1\nline2\nline3"