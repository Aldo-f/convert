from click.testing import CliRunner

from convert.cli import cli


def test_txt_to_docx(tmp_path):
    p = tmp_path / "in.txt"
    p.write_text("line one\nline two\n\nline four\n")
    out = tmp_path / "out.docx"
    r = CliRunner().invoke(cli, ["convert", str(p), str(out)])
    assert r.exit_code == 0
    assert out.exists()

    from docx import Document

    doc = Document(out)
    texts = [para.text for para in doc.paragraphs]
    assert texts == ["line one", "line two", "", "line four"]
