from qiniu import Auth, put_file, BucketManager
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

def delete_from_qiniu(remote_key: str, config: "QiniuConfig") -> bool:
    """删除七牛云存储的指定文件"""
    auth = Auth(config.access_key, config.secret_key)
    bucket_manager = BucketManager(auth)
    
    ret, info = bucket_manager.delete(config.bucket, remote_key)
    
    if info.status_code != 200:
        raise RuntimeError(f"API 错误: {info.text_body}")
    if ret is None:
        raise RuntimeError("文件不存在或删除失败")
    
    return True