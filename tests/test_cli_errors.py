"""Tests for CLI error paths and edge cases."""
from click.testing import CliRunner
from convert.cli import cli


def test_convert_no_converter(tmp_path):
    """Test convert with unsupported format pair."""
    src = tmp_path / "in.unknown"
    src.write_text("hello")
    dst = tmp_path / "out.unknown"
    runner = CliRunner()
    result = runner.invoke(cli, ["convert", str(src), str(dst)])
    assert result.exit_code != 0
    assert "No converter" in result.output


def test_check_specs_failure(tmp_path):
    """Test check_specs when a converter is missing its spec."""
    from convert.registry import registry
    # Register a fake converter with no spec
    @registry.register("fake", "fake")
    def fake(req):
        return req

    runner = CliRunner()
    result = runner.invoke(cli, ["--check-specs"])
    assert result.exit_code != 0
    assert "Spec check failed" in result.output
    # Clean up: remove fake converter to avoid polluting registry for other tests
    registry._d.pop(("fake", "fake"), None)


def test_check_specs_flag_success():
    """Test --check-specs when all specs are valid."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--check-specs"])
    assert result.exit_code == 0
    assert "All specs valid" in result.output


def test_cli_main_block():
    """Test that __main__ entry point works."""
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "convert.cli", "--version"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "convert" in result.stdout.lower()