# PicFlow

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/) [![PyPI Version](https://img.shields.io/pypi/v/picflow.svg)](https://pypi.org/project/picflow/)

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
  - [ImageMagick](https://imagemagick.org/) (scaling, optional)
  - [cwebp](https://developers.google.com/speed/webp/docs/precompiled) (WebP compression, optional)

### Install PicFlow

```bash
pip install picflow
```



## Quick Start

### Configure Qiniu

Run the following command to create config file `~/.picflow/config.yaml`：

```bash
picflow config init
```

You need to enter `ACCESS_KEY` and `SECRET_KEY` and other information. The configuration file content is as follows.

```yaml
storage:
  qiniu:
    access_key: "YOUR_ACCESS_KEY"
    secret_key: "YOUR_SECRET_KEY"
    bucket: "YOUR_BUCKET_NAME"
    domain: "https://cdn.example.com"  # CDN domain
```



### Process Images

```bash
# Compress to WebP
picflow process --format webp --quality 85 ~/images/photo.jpg

# Process entire folder recursively
picflow batch ~/gallery --scale 50% --output ~/compressed_gallery
```



### Upload Images

```bash
# Upload a image directly
picflow upload ~/images/photo.jpg

# Upload multiple images
picflow upload test.jpg test2.jpg test3.jpg

# Process and upload the image
picflow process --scale 256 --format webp --quality 85 test.jpg
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

# Print version
picflow --version

# View image properties
picflow info ~/images/photo.jpg

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
