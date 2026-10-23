import click
from pathlib import Path
from convert.registry import registry
from convert.models import ConversionRequest, ConversionResult

# Import converters to register them
import convert.converters  # noqa: F401

@click.group()
@click.version_option("0.1.0", prog_name="convert")
def cli():
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
        source_path=source,
        target_path=target,
        src_fmt=src_fmt,
        dst_fmt=dst_fmt
    )
    
    result: ConversionResult = converter(request)
    click.echo(str(result.output_path))

if __name__ == "__main__":
    cli()