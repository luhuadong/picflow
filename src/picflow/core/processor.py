from pathlib import Path
from typing import Optional, Tuple

def process_image(
    input_path: Path,
    output_path: Path,
    format: str,
    quality: int,
    scale: Optional[Tuple[int, int]],
    method: str
) -> Path:
    """
    核心图片处理函数
    返回处理后的文件路径
    """
    from ..processors.webp import compress_image
    
    # 执行压缩处理
    compress_image(
        input_path=input_path,
        output_path=output_path,
        quality=quality,
        target_format=format,
        scale=scale,
        method=method
    )
    
    return output_path