# 简介
监控平台

# 环境参考

- Python: 3.9.12

# 基础使用

### 1. 虚拟环境配置

- 在根目录下

```shell
python3 -m venv venv
echo 'export PYTHONPATH="<your_path>/vigilant"' >> venv/bin/activate
source venv/bin/activate
```

### 2. 依赖管理

> 在根目录下

- 生成：

```shell
pipreqs ./
# pipreqs 需要先下载 pip install pipreqs
```

- 拉取：

```shell
pip install -r requirements.txt t
``` 

# 运行
> venv/bin/python3 manage.py runserver 0.0.0.0:8000 