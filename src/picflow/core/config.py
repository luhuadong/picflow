from dataclasses import dataclass, field
from pathlib import Path
import yaml
from typing import Optional, Dict, Optional, Union, Type

CONFIG_DIR = Path.home() / ".picflow"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.yaml"

@dataclass
class QiniuConfig:
    access_key: str
    secret_key: str
    bucket: str
    domain: str

@dataclass
class AwsS3Config:
    access_key_id: str
    secret_access_key: str
    region: str
    bucket: str
    endpoint: Optional[str] = None

@dataclass
class ProcessingConfig:
    default_quality: int = 85
    formats: Dict[str, Dict] = field(default_factory=lambda: {
        "webp": {"method": 6},
        "jpeg": {"progressive": True}
    })

@dataclass
class AppConfig:
    default_provider: str = field(default="qiniu")  # 默认存储提供商
    storage: Dict[str, Union[QiniuConfig, AwsS3Config]] = field(default_factory=dict)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "AppConfig":
        config_path = config_path or Path.home() / ".picflow" / "config.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}

        # 解析存储提供商配置
        storage_configs = {}
        for provider, data in config_data.get("storage", {}).items():
            if provider == "qiniu":
                storage_configs[provider] = QiniuConfig(**data)
            elif provider == "aws":
                storage_configs[provider] = AwsS3Config(**data)

        # 解析默认存储提供商
        default_provider = config_data.get("default_provider", "qiniu")

        # 验证默认存储配置是否存在
        if default_provider not in storage_configs:
            available = list(storage_configs.keys())
            raise ValueError(
                f"Default provider '{default_provider}' not configured. "
                f"Available providers: {available}"
            )

        # 解析图片处理配置
        processing_data = config_data.get("processing", {})
        processing_config = ProcessingConfig(
            default_quality=processing_data.get("default_quality", 85),
            formats=processing_data.get("formats", {
                "webp": {"method": 6},
                "jpeg": {"progressive": True}
            })
        )

        return cls(
            default_provider=default_provider,
            storage=storage_configs,
            processing=processing_config
        )

    def get_provider_config(
        self, 
        provider: Optional[str] = None
    ) -> Union[QiniuConfig, AwsS3Config]:
        """获取指定存储提供商的配置（默认使用 default_provider）"""
        target_provider = provider or self.default_provider
        config = self.storage.get(target_provider)
        if not config:
            raise ValueError(
                f"Storage provider '{target_provider}' not configured. "
                f"Available providers: {list(self.storage.keys())}"
            )
        return config

    @property
    def active_provider(self) -> Type[Union[QiniuConfig, AwsS3Config]]:
        """获取当前激活的存储配置类型"""
        return type(self.get_provider_config())
