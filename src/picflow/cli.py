import click
from pathlib import Path
import yaml
from .core.config import AppConfig, CONFIG_DIR, DEFAULT_CONFIG_PATH

@click.group()
def cli():
    """PicFlow: Image processing and upload tool."""
    pass

@cli.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "-f", default="webp", help="Output format (webp/jpeg/png)")
@click.option("--quality", "-q", type=int, help="Compression quality (0-100)")
@click.option("--scale", "-s", help="缩放尺寸，例如 800x600")
@click.option("--method", "-m", default="pillow", help="压缩方式 (pillow/cli)")
@click.option("--show-qr", is_flag=True, help="Display QR code in terminal")
@click.option("--qr-file", type=click.Path(path_type=Path), help="Save QR code as PNG file")
def process(input_path: Path, format: str, quality: int, scale, method, show_qr: bool, qr_file: Path):
    """Process and upload a single image."""
    from .processors.webp import compress_image
    from .uploaders.qiniu import upload_to_qiniu

    config = AppConfig.load()
    click.echo(f"Processing {input_path}...")

    # 处理图片（假设已实现压缩函数）
    # 解析缩放尺寸
    scale_dim = tuple(map(int, scale.split("x"))) if scale else None

    # 生成输出路径
    # output_path = input_path.with_name(f"{input_path.stem}_processed.{format}")
    output_path = input_path.with_suffix(f".{format}")
    
    # 压缩图片
    try:
        compress_image(
            input_path=input_path,
            output_path=output_path,
            quality=quality or config.processing.default_quality,
            target_format=format,
            scale=scale_dim,
            method=method
        )
        click.secho(f"✅ 图片处理完成: {output_path}", fg="green")
    except Exception as e:
        click.secho(f"❌ 处理失败: {str(e)}", fg="red")
        return

    # 上传到七牛云
    try:
        qiniu_config = config.get_provider_config()
        url = upload_to_qiniu(output_path, output_path.name, qiniu_config)
        click.secho(f"✅ 上传成功！访问链接: {url}", fg="green")

        if show_qr or qr_file:
            from .utils.qr import generate_qr_terminal, generate_qr_image
            try:
                if show_qr:
                    qr_ascii = generate_qr_terminal(url)
                    click.echo("\n🔍 Scan QR Code:")
                    click.echo(qr_ascii)
            
                if qr_file:
                    generate_qr_image(url, qr_file)
                    click.secho(f"✅ QR Code saved to: {qr_file}", fg="green")
            except ImportError:
                click.secho("❌ QR 功能需要安装 qrcode 库：pip install qrcode[pil]", fg="red")
        
    except Exception as e:
        click.secho(f"❌ 上传失败: {str(e)}", fg="red")

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
