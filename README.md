# PicFlow

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

[English](README.md) | [中文](README_zh.md)

**PicFlow** is a command-line tool for automating image processing (scaling/compression) and uploading to cloud storage (e.g., Qiniu Cloud). Supports Windows, Linux, and macOS.



## Features

### 🛠️ Core Capabilities

- **Image Processing**
  - Scaling, format conversion (JPEG/PNG/WebP)
  - Quality compression (based on `cwebp` and `ImageMagick`)
- **Cloud Storage Integration**
  - Supports Qiniu Cloud, AWS S3 (planned)
  - Auto-generates CDN URLs
- **Batch Operations**
  - Recursively process folders
  - Parallel task acceleration

### 🚀 Efficiency

- **Config-Driven**: Manage cloud keys and parameters via YAML
- **Cross-Platform**: Run the same command on Windows/Linux/macOS


## Installation

### Prerequisites

- Python 3.8+
- External Tools (auto-detected):
  - [ImageMagick](https://imagemagick.org/) (scaling)
  - [cwebp](https://developers.google.com/speed/webp/docs/precompiled) (WebP compression)
  - [qshell](https://github.com/qiniu/qshell) (Qiniu upload)

### Install PicFlow

```bash
pip install picflow
```

## Quick Start

### 1. Configure Qiniu

Create config file `~/.picflow/config.yaml`：

```yaml
storage:
  qiniu:
    access_key: "YOUR_ACCESS_KEY"
    secret_key: "YOUR_SECRET_KEY"
    bucket: "YOUR_BUCKET_NAME"
    domain: "https://cdn.example.com"  # CDN domain
```

### 2. Process & Upload Images

```bash
# Compress to WebP and upload
picflow process --format webp --quality 85 ~/images/photo.jpg

# Process entire folder recursively
picflow batch ~/gallery --scale 50% --output ~/compressed_gallery
```

## Advanced Configuration

### Custom Processing

```yaml
processing:
  default_quality: 90
  formats:
    webp:
      method: 6  # Compression method level
    jpeg:
      progressive: true  # Progressive JPEG
```

### CLI Options

```bash
# Show help
picflow --help

# Override quality parameters in configuration
picflow process input.png --quality 75 --format jpeg
```

## Contributing

Issues and PRs are welcome!

- Code Style: Follow PEP8
- Testing: Add pytest unit tests
- Docs: Update English or Chinese documentation

## License

Licensed under the [MIT License](LICENSE).
