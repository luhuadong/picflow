# Changelog

## [Unreleased]
### Added
- 支持又拍云、阿里云 OSS、腾讯云 COS、AWS S3 存储

### Changed
- 重构核心配置模块，支持多环境配置

### Fixed
- 修复 WebP 压缩时 Pillow 版本兼容性问题

## [0.1.4] - 2025-03-22

### Added

- 新增 `picflow --version` 命令查看版本信息
- 增加 `picflow delete` 命令删除图床服务器中的指定图片文件
- 拆分 `picflow process` 命令，增加 `picflow upload` 上传命令

### Changed

- 删除生成二维码的 `--qr-file` 选项，仅保留 `--show-qr` 选项
- 优化图片处理后的文件名称命名规则
- 统一代码注释的中英文描述

## [0.1.3] - 2025-03-21
### Added
- 初始版本发布
- 核心功能：
  - 支持查看图片信息（EXIF 元数据）
  - 支持图片压缩（基于 Pillow）
  - 支持七牛云上传（基于 qiniu SDK）
  - 上传后生成二维码功能（基于 qrcode）