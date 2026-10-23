import sys

from click.testing import CliRunner

from convert.cli import cli


def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "convert" in result.output.lower()


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "type-x to type-y" in result.output.lower()


def test_cli_main_block():
    # Directly call cli() to cover the main block
    # We need to mock sys.argv
    original_argv = sys.argv
    try:
        sys.argv = ["convert", "--version"]
        cli(standalone_mode=False)
    except SystemExit as e:
        assert e.code == 0
    finally:
        sys.argv = original_argv
