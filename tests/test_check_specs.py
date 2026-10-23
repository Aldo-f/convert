from click.testing import CliRunner
from convert.cli import cli

def test_check_specs():
    runner = CliRunner()
    result = runner.invoke(cli, ["check-specs"])
    assert result.exit_code == 0
    assert "All specs valid" in result.output