from pathlib import Path
from click.testing import CliRunner
from convert.cli import cli

def test_txt_to_md(tmp_path):
    p = tmp_path / "in.txt"
    p.write_text("hello\n")
    out = tmp_path / "out.md"
    r = CliRunner().invoke(cli, ["convert", str(p), str(out)])
    assert r.exit_code == 0
    assert out.read_text().startswith("hello")