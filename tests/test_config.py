import pytest
from pathlib import Path
from src.picflow.core.config import AppConfig, QiniuConfig, AwsS3Config

# 测试夹具：模拟临时配置文件
@pytest.fixture
def sample_config(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_content = """
    default_provider: qiniu
    storage:
      qiniu:
        access_key: "test_ak"
        secret_key: "test_sk"
        bucket: "test-bucket"
        domain: "https://test.com"
    processing:
      default_quality: 90
    """
    config_path.write_text(config_content)
    return config_path

def test_load_config(sample_config):
    """测试配置加载基础功能"""
    config = AppConfig.load(sample_config)
    
    assert config.default_provider == "qiniu"
    assert isinstance(config.storage["qiniu"], QiniuConfig)
    assert config.processing.default_quality == 90

def test_default_provider_validation():
    """测试默认存储提供商验证逻辑"""
    invalid_config = {
        "default_provider": "aws",
        "storage": {
            "qiniu": {  # 默认提供商设为 aws，但未配置 aws
                "access_key": "ak",
                "secret_key": "sk",
                "bucket": "bucket",
                "domain": "https://test.com"
            }
        }
    }
    
    # 模拟从字典加载配置
    with pytest.raises(ValueError) as e:
        AppConfig.load_from_dict(invalid_config)  # 需要实现此方法
    
    assert "Default provider 'aws' not configured" in str(e.value)

def test_get_provider_config(sample_config):
    """测试获取指定存储配置"""
    config = AppConfig.load(sample_config)
    
    # 测试默认提供商
    qiniu = config.get_provider_config()
    assert qiniu.bucket == "test-bucket"
    
    # 测试显式指定
    qiniu = config.get_provider_config("qiniu")
    assert isinstance(qiniu, QiniuConfig)