import click
from pathlib import Path
from .core.config import AppConfig

@click.group()
def cli():
    """PicFlow: Image processing and upload tool."""
    pass

@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--format", "-f", default="webp", help="Output format (webp/jpeg/png)")
@click.option("--quality", "-q", type=int, help="Compression quality (0-100)")
def process(input_path, format, quality):
    """Process and upload a single image."""
    config = AppConfig.load()
    click.echo(f"Processing {input_path}...")

@cli.command()
@click.argument("input_dir", type=click.Path(exists=True))
@click.option("--scale", "-s", help="Scale percentage (e.g., 50%)")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
def batch(input_dir, scale, output):
    """Batch process a directory."""
    click.echo(f"Batch processing {input_dir}...")

if __name__ == "__main__":
    cli()
