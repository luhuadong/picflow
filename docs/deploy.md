# 发布软件包

## 注册 PyPI 账户

- **PyPI 生产环境**: https://pypi.org/
- **PyPI 测试环境**: https://test.pypi.org/

```bash
# 安装 twine（用于上传包）
pip install twine

# 安装构建工具
pip install build

# 生成 API Token（推荐代替密码）
# 登录 PyPI → Account Settings → API tokens → Add API Token
```



## 本地打包测试

### 安装构建工具

```bash
pip install build
```

### 生成分发包

```bash
python -m build
```

生成文件在 `dist/` 目录：

```bash
dist/
├── picflow-0.1.0.tar.gz
└── picflow-0.1.0-py3-none-any.whl
```

### 本地安装验证

```bash
pip install dist/picflow-0.1.0-py3-none-any.whl

# 验证安装
picflow --version
```



## 发布到 PyPI

### 上传到测试环境（可选）

```bash
twine upload --repository testpypi dist/*
# 使用测试环境账号或 Token
```

### 正式发布到 PyPI

```bash
twine upload dist/*
# 使用您的 PyPI 用户名和 API Token
```

上传成功

```bash
$ twine upload dist/*
Uploading distributions to https://upload.pypi.org/legacy/
Uploading picflow-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.9/12.9 kB • 00:00 • ?
Uploading picflow-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 15.5/15.5 kB • 00:00 • ?

View at:
https://pypi.org/project/picflow/0.1.0/
```

在另一环境中安装

```bash
pip install picflow
pip install --upgrade picflow         # 安装最新版本
pip install picflow==0.1.3            # 安装指定版本
pip uninstall picflow                 # 卸载
```

查看是否安装成功

```bash
pip list | grep picflow
pip freeze | grep picflow
pip show picflow
```

