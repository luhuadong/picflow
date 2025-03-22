import subprocess
from pathlib import Path
from PIL import Image  # 需要安装 Pillow
from typing import Optional, Tuple
import logging

logger = logging.getLogger("picflow.processor")

def compress_image(
    input_path: Path,
    output_path: Path,
    quality: int = 85,
    target_format: str = None,
    scale: tuple = None,
    method: str = "pillow"  # 或 "cli" 调用外部工具
) -> Path:
    """
    压缩/转换图片格式，支持缩放
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径（需包含扩展名）
        quality: 压缩质量 (1-100)
        target_format: 目标格式 (webp/jpeg/png)
        scale: 可选缩放尺寸 (宽, 高)
        method: 压缩方式 (pillow/cli)
    """
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if method == "pillow":
        return _compress_with_pillow(
            input_path, output_path, quality, target_format, scale
        )
    elif method == "cli":
        return _compress_with_cli(
            input_path, output_path, quality, target_format, scale
        )
    else:
        raise ValueError(f"Unsupported method: {method}")

def _compress_with_pillow(
    input_path: Path,
    output_path: Path,
    quality: int,
    target_format: str,
    scale: tuple
) -> Path:
    """使用 Pillow 库进行压缩和缩放"""
    try:
        with Image.open(input_path) as img:
            # 缩放处理
            if scale:
                original_width, original_height = img.size
                target_width, target_height = scale

                if target_width and target_height:
                    new_size = (target_width, target_height)
                elif target_width:
                    ratio = target_width / original_width
                    new_height = int(original_height * ratio)
                    new_size = (target_width, new_height)
                elif target_height:
                    ratio = target_height / original_height
                    new_width = int(original_width * ratio)
                    new_size = (new_width, target_height)
                else:
                    new_size = (original_width, original_height)
    
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 格式转换与保存
            save_kwargs = {"quality": quality, "optimize": True}
            if target_format.lower() == "webp":
                save_kwargs["method"] = 6  # 压缩方法级别
            if target_format.lower() == "jpg":
                target_format = "jpeg"
            img.save(output_path, format=target_format, **save_kwargs)
            return output_path
    except Exception as e:
        logger.error(f"Pillow 压缩失败: {str(e)}")
        raise RuntimeError("图片处理失败")

def _compress_with_cli(
    input_path: Path,
    output_path: Path,
    quality: int,
    target_format: str,
    scale: Optional[Tuple[int, int]]
) -> Path:
    """调用外部工具（ImageMagick/cwebp）进行压缩"""
    try:
        if target_format == "webp":
            # 使用 cwebp 压缩为 WebP
            cmd = ["cwebp", "-q", str(quality), str(input_path), "-o", str(output_path)]
            if scale:
                cmd.insert(1, "-resize")
                cmd.insert(2, f"{scale[0]} {scale[1]}")
        else:
            # 使用 ImageMagick 处理其他格式
            scale_option = f"-resize {scale[0]}x{scale[1]}" if scale else ""
            cmd = [
                "convert",
                str(input_path),
                scale_option,
                "-quality",
                str(quality),
                str(output_path)
            ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"CLI 工具错误: {e.stderr.decode()}")
        raise RuntimeError("外部工具执行失败")
    except FileNotFoundError:
        logger.error("未找到 ImageMagick 或 cwebp，请先安装")
        raise RuntimeError("依赖工具未安装")