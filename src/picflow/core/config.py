from dataclasses import dataclass
from pathlib import Path
import yaml
from typing import Optional, Dict

CONFIG_DIR = Path.home() / ".picflow"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.yaml"

@dataclass
class QiniuConfig:
    access_key: str
    secret_key: str
    bucket: str
    domain: str

@dataclass
class ProcessingConfig:
    default_quality: int = 85
    formats: Dict[str, Dict] = None

@dataclass
class AppConfig:
    qiniu: Optional[QiniuConfig] = None
    processing: ProcessingConfig = ProcessingConfig()

    @classmethod
    def load(cls, config_path: Path = None) -> "AppConfig":
        default_path = Path.home() / ".picflow" / "config.yaml"
        config_path = config_path or default_path

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        qiniu_data = data.get("storage", {}).get("qiniu", {})
        qiniu = QiniuConfig(**qiniu_data) if qiniu_data else None

        processing_data = data.get("processing", {})
        processing = ProcessingConfig(
            default_quality=processing_data.get("default_quality", 85),
            formats=processing_data.get("formats", {})
        )

        return cls(qiniu=qiniu, processing=processing)
