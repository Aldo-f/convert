from pathlib import Path
from click.testing import CliRunner
from convert.cli import cli

def test_auto_detect_md_to_docx(tmp_path):
    """Test auto-detection of md format from extension."""
    md = tmp_path / "test.md"
    md.write_text("# Title\n\nContent")
    out = tmp_path / "test.docx"
    r = CliRunner().invoke(cli, ["convert", str(md), str(out)])
    assert r.exit_code == 0
    assert out.exists()

def test_auto_detect_txt_to_md(tmp_path):
    """Test auto-detection of txt format from extension."""
    txt = tmp_path / "test.txt"
    txt.write_text("hello world")
    out = tmp_path / "test.md"
    r = CliRunner().invoke(cli, ["convert", str(txt), str(out)])
    assert r.exit_code == 0
    assert out.read_text() == "hello world"

def test_unknown_extension_fails(tmp_path):
    """Test that unknown extension fails with helpful error."""
    unknown = tmp_path / "test.xyz"
    unknown.write_text("content")
    out = tmp_path / "test.md"
    r = CliRunner().invoke(cli, ["convert", str(unknown), str(out)])
    assert r.exit_code != 0
    assert "No converter registered for xyz" in r.output