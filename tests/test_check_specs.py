from click.testing import CliRunner
from convert.cli import cli

def test_check_specs_subcommand():
    runner = CliRunner()
    result = runner.invoke(cli, ["check-specs"])
    assert result.exit_code == 0
    assert "All specs valid" in result.output

def test_check_specs_flag_success():
    runner = CliRunner()
    result = runner.invoke(cli, ["--check-specs"])
    assert result.exit_code == 0
    assert "All specs valid" in result.output

def test_check_specs_flag_failure(monkeypatch):
    def fake_check_specs():
        return False
    monkeypatch.setattr("convert.cli._check_specs", fake_check_specs)
    runner = CliRunner()
    result = runner.invoke(cli, ["--check-specs"])
    assert result.exit_code != 0
    stderr = (result.stderr_bytes or b"").decode()
    assert "Spec check failed" in stderr
