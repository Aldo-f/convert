from click.testing import CliRunner

from convert.cli import cli


def test_md_to_txt(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text(
        "# Heading\n\n"
        "This is **bold** and *italic* text.\n\n"
        "Visit [Example](https://example.com) for details.\n\n"
        "| Col A | Col B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        "```python\nprint('hi')\n```\n"
    )
    out = tmp_path / "doc.txt"
    result = CliRunner().invoke(cli, ["convert", str(md), str(out)])
    assert result.exit_code == 0
    assert out.exists()

    text = out.read_text(encoding="utf-8")

    # Plain text: no Markdown syntax remnants.
    assert "#" not in text
    assert "**" not in text
    assert "`" not in text
    assert "|---|---|" not in text
    assert "---" not in text

    # Required words remain.
    assert "Heading" in text
    assert "bold" in text
    assert "italic" in text
    assert "Example" in text
    assert "https://example.com" not in text  # link URL stripped, text kept
    assert "Col A | Col B" in text
    assert "1 | 2" in text
    assert "print('hi')" in text
