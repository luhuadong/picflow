# 测试



## 准备测试环境

### 1.1 安装测试依赖

确保项目依赖包含 `pytest`，在项目根目录执行：

```bash
pip install -r requirements.txt  # 确保 requirements.txt 包含 pytest
# 或单独安装
pip install pytest pytest-mock
```

### 1.2 项目结构验证

确认测试目录结构符合 pytest 规范：

```bash
picflow/
├── src/
│   └── picflow/       # 源代码
└── tests/             # 测试代码
    ├── __init__.py    # 空文件（标记为 Python 包）
    ├── conftest.py    # 测试配置（可选）
    └── test_config.py # 配置模块测试
```

## 运行测试

### 3.1 基础运行方式

在项目根目录执行：

```bash
pytest tests/
```

### 3.2 常用参数

| 参数                | 说明                                | 示例                       |
| :------------------ | :---------------------------------- | :------------------------- |
| `-v`                | 显示详细输出                        | `pytest -v tests/`         |
| `--cov=src/picflow` | 生成覆盖率报告（需安装 pytest-cov） | `pytest --cov=src/picflow` |
| `-k EXPRESSION`     | 按名称过滤测试用例                  | `pytest -k "config"`       |
| `--lf`              | 只运行上次失败的测试                | `pytest --lf`              |

### 3.3 带覆盖率报告

```bash
pip install pytest-cov
pytest --cov=src/picflow --cov-report=html
```

报告将生成在 `htmlcov/` 目录，用浏览器打开 `htmlcov/index.html` 查看详情。