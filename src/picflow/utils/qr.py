import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from io import StringIO
import sys
from pathlib import Path

def generate_qr_terminal(url: str) -> str:
    """生成终端友好的 ASCII 二维码"""
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make()
    buffer = StringIO()
    qr.print_ascii(out=buffer, invert=True)
    return buffer.getvalue()

def generate_qr_image(url: str, output_path: Path, style: str = "rounded"):
    """生成带样式的二维码图片"""
    qr = qrcode.QRCode(
        version=7,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4
    )
    qr.add_data(url)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        embeded_image_path="logo.png" if style == "with_logo" else None
    )
    img.save(str(output_path))