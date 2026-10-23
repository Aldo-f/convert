from pathlib import Path

import click

# Import converters to register them
import convert.converters  # noqa: F401
from convert.models import ConversionRequest, ConversionResult
from convert.registry import registry


def _check_specs():
    """Check that all registered converters have spec.md files with required sections."""
    required_sections = ["## Input", "## Output", "## Dependencies"]
    missing = []

    for src, dst in registry.list_pairs():
        # Find the converter module
        converter_name = f"{src}_to_{dst}"
        try:
            module = __import__(f"convert.converters.{converter_name}", fromlist=[""])
            # spec.md is in a subdirectory named after the converter
            spec_path = Path(module.__file__).parent / converter_name / "spec.md"
            # Also check legacy location (same directory as module)
            if not spec_path.exists():
                spec_path = Path(module.__file__).parent / "spec.md"
        except (ImportError, AttributeError):
            missing.append(f"{src}→{dst}: no converter module found")
            continue

        if not spec_path.exists():
            missing.append(f"{src}→{dst}: spec.md not found at {spec_path}")
            continue

        content = spec_path.read_text()
        for section in required_sections:
            if section not in content:
                missing.append(f"{src}→{dst}: missing required section '{section}'")

    if missing:
        for m in missing:
            click.echo(f"Spec check failed: {m}", err=True)
        return False
    return True


def _check_specs_flag(ctx, param, value):
    """Eager --check-specs flag: run spec check and exit."""
    if not value or ctx.resilient_parsing:
        return
    if _check_specs():
        click.echo("All specs valid")
        ctx.exit(0)
    click.echo("Spec check failed", err=True)
    ctx.exit(1)


class ConvertGroup(click.Group):
    """Click group that also supports direct ``convert <source> <target>``.

    Because ``convert`` is the group entry point (and also has a ``convert``
    subcommand), an unrecognized first argument that is followed by a target
    is routed to the ``convert`` subcommand instead of erroring.
    """

    def resolve_command(self, ctx, args):
        if not args:
            return super().resolve_command(ctx, args)

        cmd_name = args[0]
        cmd = self.get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd_name, cmd, args[1:]

        # Unknown first argument: treat as direct conversion
        # `convert <source> <target>`.
        if len(args) >= 2:
            convert_cmd = self.get_command(ctx, "convert")
            if convert_cmd is not None:
                return cmd_name, convert_cmd, args[:2]

        return super().resolve_command(ctx, args)


@click.group(cls=ConvertGroup, invoke_without_command=True)
@click.version_option("0.1.0", prog_name="convert")
@click.option(
    "--check-specs",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=_check_specs_flag,
    help="Check all converter specs and exit.",
)
@click.pass_context
def cli(ctx):
    """convert: type-x to type-y converter."""


@cli.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.argument("target", type=click.Path(path_type=Path))
def convert(source: Path, target: Path):
    """Convert a file from one format to another."""
    src_fmt = source.suffix.lstrip(".")
    dst_fmt = target.suffix.lstrip(".")

    converter = registry.get(src_fmt, dst_fmt)
    if converter is None:
        click.echo(f"Error: No converter registered for {src_fmt} -> {dst_fmt}", err=True)
        raise click.Abort()

    request = ConversionRequest(
        source_path=source, target_path=target, src_fmt=src_fmt, dst_fmt=dst_fmt
    )

    result: ConversionResult = converter(request)
    click.echo(str(result.output_path))


@cli.command()
def check_specs():
    """Verify all registered converters have valid spec.md files."""
    if not _check_specs():
        raise click.Abort()
    click.echo("All specs valid")


if __name__ == "__main__":
    cli()
