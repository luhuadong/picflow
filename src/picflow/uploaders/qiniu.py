from qiniu import Auth, put_file, BucketManager
from pathlib import Path

def upload_to_qiniu(
    local_path: Path,
    remote_key: str,
    config: "QiniuConfig",
    overwrite: bool = False
) -> str:
    """使用七牛云 Python SDK 上传文件"""
    auth = Auth(config.access_key, config.secret_key)

    # 检查文件冲突
    if not overwrite:
        bucket_manager = BucketManager(auth)
        ret, _ = bucket_manager.stat(config.bucket, remote_key)
        if ret is not None:
            raise FileExistsError(f"远程文件 {remote_key} 已存在")
    
    # 生成上传凭证
    token = auth.upload_token(config.bucket, key=remote_key)

    # 执行上传
    ret, info = put_file(
        token,
        remote_key,
        str(local_path),
        version='v2'
    )

    if info.status_code != 200 or ret.get("key") != remote_key:
        raise RuntimeError(f"上传失败: {info.text_body}")

    return f"{config.domain}/{remote_key}"

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