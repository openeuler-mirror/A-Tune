# tuning

#### 介绍
性能优化

#### 软件架构
软件架构说明


#### 安装教程

1. clone本仓库 
2. 安装依赖库
```bash
yum install python3-devel krb5-devel
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install fastapi pydantic uvicorn
pip3 install gssapi
deactivate
```

#### 使用说明

1.  准备env yaml，放入 config/.env.yaml，例如：
```YAML
servers:
    -
        "ip": "9.82.196.9",
        "password": "Huawei12#$"

UVICORN_IP: "0.0.0.0"
UVICORN_PORT: 8100

REMOTE_EMBEDDING_ENDPOINT: "https://open.bigmodel.cn/api/paas/v4/embeddings"

LLM_URL: "http://9.82.33.59:11434/v1"
LLM_MODEL_NAME: "qwen2:72b"
LLM_MAX_TOKENS: "4096"
```

2.  调优server安装依赖包：
```BASH
yum install sysstat perf
systemctl start sysstat
```

3.  运行EulerCopilot
```bash
export PYTHONPATH="`pwd`:$PYTHONPATH"
python3 src/testmain.py
```
