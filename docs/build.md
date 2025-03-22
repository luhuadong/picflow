# PicFlow 构建



## 开发环境

安装依赖

```bash
pip install -r requirements.txt
```

本地安装，进入项目根目录，执行：

```bash
pip install -e .
```

彻底卸载旧版本

```bash
pip uninstall picflow -y
```

查看帮助

```bash
picflow --help
```

测试 process 命令

```bash
picflow process ~/test.jpg --format webp
```



## 创建配置文件

```bash
mkdir -p ~/.picflow
echo 'storage:
  qiniu:
    access_key: "test"
    secret_key: "test"
    bucket: "test-bucket"
    domain: "https://cdn.example.com"
processing:
  default_quality: 90' > ~/.picflow/config.yaml
```

也可以通过命令创建配置文件：

```bash
picflow config init
```



## 运行测试

```bash
pytest tests/
```
