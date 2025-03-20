from click.testing import CliRunner
from src.picflow.cli import cli
from pathlib import Path

def test_config_init(tmp_path, mocker):
    """测试交互式配置初始化"""
    runner = CliRunner()
    
    # 模拟用户输入
    inputs = [
        "qiniu",        # 选择存储提供商
        "test_ak",      # Access Key
        "test_sk",      # Secret Key
        "test-bucket",  # Bucket
        "https://test.com", # Domain
        "90"            # 默认质量
    ]
    
    # Mock keyring 避免影响系统密钥环
    mocker.patch("keyring.set_password")
    mocker.patch("keyring.get_password", return_value="mock_encrypted")
    
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # 运行命令并模拟输入
        result = runner.invoke(
            cli, ["config", "init"],
            input="\n".join(inputs)
        )
        
        assert "Configuration saved" in result.output
        assert (Path.home() / ".picflow/config.yaml").exists()
