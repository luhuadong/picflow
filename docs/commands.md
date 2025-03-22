# PicFlow 命令



## 处理

测试 process 命令

```bash
picflow process test.png --format webp
picflow process ~/Pictures/test.jpg --format webp --quality 90
```

创建配置文件：

```bash
picflow config init
```

显示二维码

```bash
picflow process test.png --format webp --show-qr       # 终端显示二维码
picflow process test.png --qr-file qrcode.png          # 保存为 PNG 文件
```



## 删除

```bash
# 删除单个文件
picflow delete example.jpg

# 批量删除
picflow delete dir/example1.jpg dir/example2.jpg

# 强制删除（无需确认）
picflow delete example.jpg --force
```

