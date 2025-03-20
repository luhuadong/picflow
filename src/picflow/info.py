from pathlib import Path
from PIL import Image
import exifread
import os
from typing import Dict, Optional

def get_image_info(image_path: Path) -> Dict[str, str]:
    """获取图片基础信息和 EXIF 元数据"""
    info = {}
    
    # 基础信息
    info["path"] = str(image_path.resolve())
    info["file_size"] = f"{os.path.getsize(image_path) / 1024:.2f} KB"
    
    with Image.open(image_path) as img:
        # 格式与分辨率
        info["format"] = img.format
        info["resolution"] = f"{img.width}x{img.height}"
        
        # EXIF 元数据（兼容不同格式）
        exif_data = _get_exif_data(image_path)
        info.update(_parse_exif(exif_data))
    
    return info

def _get_exif_data(image_path: Path) -> Optional[dict]:
    """读取 EXIF 数据（兼容 Pillow 和 exifread）"""
    try:
        # Pillow 方式读取
        with Image.open(image_path) as img:
            exif = img.getexif()
            if exif:
                return {exif.get(tag): value for tag, value in exif.items()}
    except Exception:
        pass
    
    # exifread 补充读取
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        return {str(k): str(v) for k, v in tags.items() if not k.startswith('Thumbnail')}

def _parse_exif(exif: dict) -> Dict[str, str]:
    """解析关键 EXIF 标签"""
    mapping = {
        # 常用标签
        "DateTime": "拍摄时间",
        "Make": "设备品牌",
        "Model": "设备型号",
        "GPSLatitude": "纬度",
        "GPSLongitude": "经度",
        "Artist": "作者",
        "Copyright": "版权信息",
        "Software": "编辑软件",
        "ImageDescription": "图片描述",
        
        # EXIF 标签 ID（十进制）
        271: "设备品牌",    # Make
        272: "设备型号",    # Model
        306: "拍摄时间",    # DateTime
        33432: "版权信息",  # Copyright
    }
    
    parsed = {}
    for key, value in exif.items():
        # 优先标签名，其次标签 ID
        label = mapping.get(key) or mapping.get(int(key)) if key.isdigit() else None
        if label:
            parsed[label] = str(value)
    
    # GPS 坐标转换（示例：需要自行实现）
    if "纬度" in parsed and "经度" in parsed:
        parsed["位置"] = _convert_gps_coordinates(
            parsed["纬度"], parsed["经度"]
        )
    
    return parsed

def _convert_gps_coordinates(gps_lat: str, gps_lng: str) -> str:
    """将度分秒格式转换为十进制"""
    def dms_to_decimal(dms: str, ref: str) -> float:
        degrees, minutes, seconds = [float(x) for x in dms.strip('[]').split(', ')]
        decimal = degrees + minutes/60 + seconds/3600
        return -decimal if ref in ['S', 'W'] else decimal
    
    # 示例输入格式（需根据实际 EXIF 数据结构调整）
    lat = dms_to_decimal("22.5431", "N")  # 实际需要解析度分秒值
    lng = dms_to_decimal("114.0573", "E")
    return f"{lat:.4f}°N, {lng:.4f}°E"