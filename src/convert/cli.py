import click

@click.group()
@click.version_option("0.1.0", prog_name="convert")
def cli():
    """convert: type-x to type-y converter."""

if __name__ == "__main__":
    cli()