from pathlib import Path
from click.testing import CliRunner
from convert.cli import cli

def test_md_to_docx(tmp_path):
    md = tmp_path / "t.md"
    md.write_text("# Title\n\n**Bold** and *italic*.\n\n| A | B |\n|---|---|\n| 1 | 2 |\n")
    out = tmp_path / "t.docx"
    r = CliRunner().invoke(cli, ["convert", str(md), str(out)])
    assert r.exit_code == 0
    assert out.exists()
    # verify content via docx lib
    from docx import Document as Doc
    doc = Doc(str(out))
    texts = [p.text for p in doc.paragraphs]
    assert any("Title" in t for t in texts)