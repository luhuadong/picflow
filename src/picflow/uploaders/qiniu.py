from qiniu import Auth, put_file
from pathlib import Path

def upload_to_qiniu(local_path: Path, remote_key: str, config: "QiniuConfig") -> str:
    """使用七牛云 Python SDK 上传文件"""
    auth = Auth(config.access_key, config.secret_key)
    token = auth.upload_token(config.bucket, key=remote_key)

    ret, info = put_file(
        token,
        remote_key,
        str(local_path),
        version='v2'
    )

    if ret and ret.get('key') == remote_key:
        return f"{config.domain}/{remote_key}"
    else:
        raise RuntimeError(f"上传失败: {info.text_body}")