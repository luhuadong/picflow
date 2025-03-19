# PicFlow 图片处理与上传工作流工具

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

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
  - [ImageMagick](https://imagemagick.org/)（用于缩放）
  - [cwebp](https://developers.google.com/speed/webp/docs/precompiled)（WebP 压缩）
  - [qshell](https://github.com/qiniu/qshell)（七牛云上传）

### 安装 PicFlow

```bash
pip install picflow
```



## 快速开始

### 1. 配置七牛云

创建配置文件 `~/.picflow/config.yaml`：

```yaml
storage:
  qiniu:
    access_key: "YOUR_ACCESS_KEY"
    secret_key: "YOUR_SECRET_KEY"
    bucket: "YOUR_BUCKET_NAME"
    domain: "https://cdn.example.com"  # CDN 域名
```

### 2. 处理并上传图片

```bash
# 压缩为 WebP 并上传
picflow process --format webp --quality 85 ~/images/photo.jpg

# 递归处理整个文件夹
picflow batch ~/gallery --scale 50% --output ~/compressed_gallery
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
