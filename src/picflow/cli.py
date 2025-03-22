import click
from pathlib import Path
import yaml, os
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
@click.option("--keep", is_flag=True, help="保留处理后的文件")
@click.option("--show-qr", is_flag=True, help="Display QR code in terminal")
def upload(local_paths, format, quality, scale, method, remote_dir, force, keep, show_qr):
    """上传图片（可选处理）"""
    from .core.config import AppConfig
    from .core.processor import process_image
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
                final_file = Path(local_path)
                
                # 需要处理时生成临时文件
                if need_processing:
                    if not format:
                        format = local_path.suffix[1:].lower()

                    output_path = _generate_processed_name(
                        original_path = local_path,
                        target_format = format,
                        scale_str = scale
                    )

                    output_path = _generate_output_path(local_path, format)
                    click.secho(f" output_path - {output_path}", fg="yellow")

                    process_image(
                        input_path = local_path,
                        output_path = output_path,
                        format = format,
                        quality = quality or config.processing.default_quality,
                        scale = _parse_scale(scale),
                        method = method
                    )
                    final_path = output_path
                    final_file = os.path.basename(output_path)

                # 生成远程路径
                remote_key = f"{remote_dir}/{final_file}" if remote_dir else final_file
                
                # 执行上传
                url = upload_to_qiniu(
                    local_path = final_path,
                    remote_key = remote_key,
                    config = qiniu_config,
                    overwrite = force
                )
                
                success.append(url)
            except Exception as e:
                failed.append((str(local_path), str(e)))
            finally:
                # 清理临时文件
                if need_processing and final_path.exists():
                    if not keep and final_path != local_path:
                        final_path.unlink()
                
                bar.update(1)

    # 输出结果
    _print_upload_results(success, failed, show_qr)

def _generate_output_path(original_path: Path, target_format: str) -> Path:
    """生成处理后的临时文件路径"""
    temp_dir = Path("/tmp/picflow_processed")
    temp_dir.mkdir(exist_ok = True)
    return temp_dir / f"{original_path.stem}_processed.{target_format}"

def _generate_processed_name(
    original_path: Path,
    target_format: str,
    scale_str: str = None
) -> str:
    """生成带缩放标记的文件名"""
    stem = original_path.stem
    orig_suffix = original_path.suffix[1:]  # 去掉点号
    
    # 添加缩放标记
    scale_mark = f"_{scale_str}" if scale_str else ""
    
    # 确定格式后缀
    format_suffix = target_format.lower() if target_format else orig_suffix
    
    # 构建文件名
    if target_format and (target_format != orig_suffix):
        return f"{stem}{scale_mark}.{format_suffix}"
    else:
        return f"{stem}{scale_mark}{original_path.suffix}"

def _parse_scale(scale: str) -> tuple:
    """解析缩放参数，返回 (width, height)，允许为None"""
    if not scale:
        return (None, None)
    
    parts = scale.lower().split('x')
    
    try:
        if len(parts) == 1:
            # 格式：256 → 宽度固定，高度按比例
            return (int(parts[0]), None)
        elif len(parts) == 2:
            # 格式：256x 或 x256 或 256x128
            width = int(parts[0]) if parts[0] else None
            height = int(parts[1]) if parts[1] else None
            return (width, height)
        else:
            raise ValueError(f"Invalid scale format: {scale}")
    except ValueError:
        raise click.BadParameter("缩放参数必须是数字组合（如 256 或 256x128）")

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
@click.option("--format", "-f", type=str, help="输出格式 (webp/jpeg/png)")
@click.option("--quality", "-q", type=int, help="压缩质量 (0-100)")
@click.option("--scale", "-s", help="缩放尺寸 (如 800x600)")
@click.option("--method", "-m", default="pillow", help="压缩方式 (pillow/cli)")
@click.option("--output", "-o", type=click.Path(), help="输出目录")
def process(input_path, format, quality, scale, method, output):

    if (not format) and (not quality) and (not scale):
        click.secho(f"🚀 无需处理，直接退出", fg="yellow")
        return

    """处理图片但不自动上传"""
    from .core.processor import process_image
    from .core.config import AppConfig

    config = AppConfig.load()
    
    try:
        # 生成输出路径
        if not format:
            format = input_path.suffix[1:].lower()

        new_name = _generate_processed_name (
            original_path = input_path,
            target_format = format,
            scale_str = scale
        )

        output_dir = Path(output) if output else input_path.parent
        output_path = output_dir / new_name
        
        # 处理图片
        result_path = process_image(
            input_path = input_path,
            output_path = output_path,
            format = format,
            quality = quality or config.processing.default_quality,
            scale = _parse_scale(scale),
            method = method
        )
        
        click.secho(f"✅ 处理完成: {result_path}", fg="green")
    except Exception as e:
        click.secho(f"❌ 处理失败: {str(e)}", fg="red")

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
