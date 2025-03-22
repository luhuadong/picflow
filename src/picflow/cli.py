import click
from pathlib import Path
import yaml
from .core.config import AppConfig, CONFIG_DIR, DEFAULT_CONFIG_PATH
from picflow import __version__
from datetime import datetime

@click.group()
@click.version_option(__version__, "--version", "-V", message="picflow, version %(version)s")
def cli():
    """PicFlow: Image processing and upload tool."""
    pass

@cli.command()
@click.argument("local_paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option("--format", "-f", help="处理格式 (webp/jpeg/png)")
@click.option("--quality", "-q", type=int, help="压缩质量 (0-100)")
@click.option("--scale", "-s", help="缩放尺寸 (如 800x600)")
@click.option("--method", "-m", default="pillow", help="压缩方式 (pillow/cli)")
@click.option("--remote-dir", "-d", default="", help="远程存储目录")
@click.option("--force", is_flag=True, help="覆盖远程同名文件")
@click.option("--show-qr", is_flag=True, help="Display QR code in terminal")
def upload(local_paths, format, quality, scale, method, remote_dir, force, show_qr: bool):
    """上传图片（可选处理）"""
    from .core.config import AppConfig
    from .processors.webp import compress_image
    from .uploaders.qiniu import upload_to_qiniu

    config = AppConfig.load()
    qiniu_config = config.get_provider_config()

    # 参数校验
    if not local_paths:
        click.secho("❌ 请指定至少一个文件", fg="red")
        return

    # 处理参数存在性检查
    need_processing = any([format, quality, scale])

    # 进度条初始化
    with click.progressbar(
        length=len(local_paths),
        label="上传进度",
        show_percent=True,
        show_eta=True
    ) as bar:
        success, failed = [], []
        for local_path in local_paths:
            try:
                # 生成最终文件路径
                final_path = Path(local_path)
                
                # 需要处理时生成临时文件
                if need_processing:
                    output_path = _generate_output_path(local_path, format)
                    compress_image(
                        input_path=local_path,
                        output_path=output_path,
                        quality=quality or config.processing.default_quality,
                        target_format=format,
                        scale=_parse_scale(scale),
                        method=method
                    )
                    final_path = output_path

                # 生成远程路径
                remote_key = _generate_remote_key(final_path, remote_dir)
                
                # 执行上传
                url = upload_to_qiniu(
                    local_path=final_path,
                    remote_key=remote_key,
                    config=qiniu_config,
                    overwrite=force
                )
                
                success.append(url)
            except Exception as e:
                failed.append((str(local_path), str(e)))
            finally:
                # 清理临时文件
                if need_processing and final_path.exists():
                    final_path.unlink()
                
                bar.update(1)

    # 输出结果
    _print_upload_results(success, failed, show_qr)

def _generate_output_path(original_path: Path, target_format: str) -> Path:
    """生成处理后的临时文件路径"""
    temp_dir = Path("/tmp/picflow_processed")
    temp_dir.mkdir(exist_ok=True)
    return temp_dir / f"{original_path.stem}_processed.{target_format}"

def _parse_scale(scale: str) -> tuple:
    """解析缩放参数"""
    return tuple(map(int, scale.split("x"))) if scale else None

def _generate_remote_key(file_path: Path, remote_dir: str) -> str:
    """生成远程存储路径"""
    timestamp = datetime.now().strftime("%Y%m%d")
    base_name = f"{timestamp}_{file_path.name}"
    return f"{remote_dir}/{base_name}" if remote_dir else base_name

def _print_upload_results(success: list, failed: list, show_qr: bool):
    """格式化输出上传结果"""
    if success:
        click.secho("\n✅ 上传成功:", fg="green")
        for url in success:
            click.echo(f"  - {url}")
            if show_qr:
                _show_qrcode(url)
    if failed:
        click.secho("\n❌ 上传失败:", fg="red")
        for path, err in failed:
            click.echo(f"  - {path} ({err})")

def _show_qrcode(url):
    """生成URL二维码"""
    from .utils.qr import generate_qr_terminal, generate_qr_image
    try:
        qr_ascii = generate_qr_terminal(url)
        click.echo("\n🔍 Scan QR Code:")
        click.echo(qr_ascii)
    except ImportError:
        click.secho("❌ QR 功能需要安装 qrcode 库：pip install qrcode[pil]", fg="red")

@cli.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "-f", default="webp", help="Output format (webp/jpeg/png)")
@click.option("--quality", "-q", type=int, help="Compression quality (0-100)")
@click.option("--scale", "-s", help="缩放尺寸，例如 800x600")
@click.option("--method", "-m", default="pillow", help="压缩方式 (pillow/cli)")
def process(input_path: Path, format: str, quality: int, scale, method):
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

@cli.command()
@click.argument("image_path", type=click.Path(exists=True, path_type=Path))
def info(image_path: Path):
    """View image details (supports PNG/JPEG/WebP)"""
    from .info import get_image_info
    
    try:
        info = get_image_info(image_path)
        click.echo("\n📷 图片信息:")
        for key, value in info.items():
            click.secho(f"▸ {key:12}: ", fg="cyan", nl=False)
            click.echo(value)
    except Exception as e:
        click.secho(f"❌ 读取失败: {str(e)}", fg="red")

@cli.command()
@click.argument("remote_keys", nargs=-1, required=True)
@click.option("--force", "-f", is_flag=True, help="跳过确认提示")
def delete(remote_keys, force):
    """删除指定远程文件"""
    from .core.config import AppConfig
    from .uploaders.qiniu import delete_from_qiniu

    config = AppConfig.load().get_provider_config()

    # 确认操作（除非强制模式）
    if not force:
        click.secho("⚠️  即将删除以下文件：", fg="yellow")
        for key in remote_keys:
            click.echo(f"  - {key}")
        click.confirm("确认删除？", abort=True)

    # 执行删除
    success = []
    failed = []
    for key in remote_keys:
        try:
            delete_from_qiniu(key, config)
            success.append(key)
        except Exception as e:
            failed.append((key, str(e)))

    # 输出结果
    if success:
        click.secho(f"✅ 成功删除 {len(success)} 个文件：", fg="green")
        for key in success:
            click.echo(f"  - {key}")
    if failed:
        click.secho(f"❌ 删除失败 {len(failed)} 个文件：", fg="red")
        for key, err in failed:
            click.echo(f"  - {key} ({err})")

if __name__ == "__main__":
    cli()
