import click
from pathlib import Path
import yaml
from .core.config import AppConfig, CONFIG_DIR, DEFAULT_CONFIG_PATH

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

@cli.group()
def config():
    """Manage PicFlow configurations."""
    pass

@config.command()
@click.option("--force", is_flag=True, help="Overwrite existing config file.")
def init(force):
    """Initialize configuration file interactively."""
    config_data = {}

    click.echo("\n🛠️  Let's configure PicFlow!\n")

    # Qiniu Cloud 配置
    click.echo("🌩️  Qiniu Cloud Configuration")
    config_data["storage"] = {
        "qiniu": {
            "access_key": click.prompt("Access Key", type=str),
            "secret_key": click.prompt("Secret Key", hide_input=True),
            "bucket": click.prompt("Bucket Name"),
            "domain": click.prompt("CDN Domain (e.g., https://cdn.example.com)")
        }
    }

    # 图片处理默认参数
    click.echo("\n🖼️  Image Processing Defaults")
    config_data["processing"] = {
        "default_quality": click.prompt(
            "Default Quality (1-100)", 
            type=click.IntRange(1, 100), 
            default=85
        ),
        "formats": {
            "webp": {"method": 6},
            "jpeg": {"progressive": True}
        }
    }

    # 创建配置目录
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # 检查文件是否存在
    if DEFAULT_CONFIG_PATH.exists() and not force:
        click.confirm(
            f"Config file {DEFAULT_CONFIG_PATH} exists. Overwrite?", 
            abort=True
        )

    # 写入文件
    with open(DEFAULT_CONFIG_PATH, "w") as f:
        yaml.safe_dump(config_data, f, sort_keys=False)
    
    click.secho(
        f"\n✅ Configuration saved to {DEFAULT_CONFIG_PATH}", 
        fg="green"
    )

if __name__ == "__main__":
    cli()
