# PicFlow 图片处理与上传工作流工具

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/) [![PyPI Version](https://img.shields.io/pypi/v/picflow.svg)](https://pypi.org/project/picflow/)

[English](README.md) | [中文](README_zh.md)

**PicFlow** 是一个命令行工具，用于自动化处理（缩放/压缩）图片并上传到云存储平台（如七牛云）。支持 Windows、Linux 和 macOS。

## 功能特性

### 🛠️ 核心功能

- **图片处理**
  - 缩放、格式转换（JPEG/PNG/WebP）
  - 质量压缩（基于 `cwebp` 和 `ImageMagick`）
- **云存储集成**
  - 支持七牛云（Qiniu）、AWS S3（计划中）
  - 自动生成 CDN 访问链接
- **批量操作**
  - 递归处理文件夹内所有图片
  - 并行任务加速

### 🚀 效率提升

- **配置文件驱动**：通过 YAML 文件管理云存储密钥和处理参数
- **跨平台**：无需修改代码，同一命令在 Windows/Linux/macOS 运行



## 安装指南

### 前置依赖

- Python 3.8+
- 外部工具（自动检测）：
  - [ImageMagick](https://imagemagick.org/)（用于缩放，可选）
  - [cwebp](https://developers.google.com/speed/webp/docs/precompiled)（WebP 压缩，可选）

### 安装 PicFlow

```bash
pip install picflow
```



## 快速开始

### 配置七牛云

执行如下命令创建配置文件 `~/.picflow/config.yaml`：

```bash
picflow config init
```

你将通过交互方式输入 `ACCESS_KEY` 和 `SECRET_KEY` 等信息，配置文件内容如下。

```yaml
storage:
  qiniu:
    access_key: "YOUR_ACCESS_KEY"
    secret_key: "YOUR_SECRET_KEY"
    bucket: "YOUR_BUCKET_NAME"
    domain: "https://cdn.example.com"  # CDN 域名
```



### 处理图片

```bash
# 压缩为 WebP 并上传
picflow process --format webp --quality 85 ~/images/photo.jpg

# 递归处理整个文件夹
picflow batch ~/gallery --scale 50% --output ~/compressed_gallery
```



### 上传图片

```bash
# 直接上传图片
picflow upload ~/images/photo.jpg

# 同时上传多张图片
picflow upload test.jpg test2.jpg test3.jpg

# 先处理后上传图片
picflow process --scale 256 --format webp --quality 85 test.jpg
```



## 高级配置

### 自定义处理参数

```yaml
processing:
  default_quality: 90
  formats:
    webp:
      method: 6  # 压缩算法级别
    jpeg:
      progressive: true  # 渐进式 JPEG
```

### 命令行参数

```bash
# 查看帮助
picflow --help

# 打印版本信息
picflow --version

# 查看图片详情
picflow info ~/images/photo.jpg

# 覆盖配置中的质量参数
picflow process input.png --quality 75 --format jpeg
```



## 贡献指南

欢迎提交 Issue 或 Pull Request！

- 代码规范：遵循 PEP8
- 测试：添加 pytest 单元测试
- 文档：更新对应的中英文内容



## 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。
