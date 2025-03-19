import subprocess
from pathlib import Path
from ..core.config import QiniuConfig

def upload_to_qiniu(local_path: Path, remote_key: str, config: QiniuConfig):
    """调用 qshell 上传文件到七牛云"""
    cmd = [
        "qshell", "fput",
        config.bucket,
        remote_key,
        str(local_path)
    ]
    try:
        subprocess.run(cmd, check=True)
        return f"{config.domain}/{remote_key}"
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"上传失败: {str(e)}")