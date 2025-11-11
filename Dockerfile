# 使用Python 3.11.6官方镜像
FROM python:3.11.6-slim

# 设置工作目录
WORKDIR /euler-copilot-tune

# 复制文件
COPY ./ .

# 配置阿里巴巴APT镜像源
RUN echo > /etc/apt/sources.list.d/debian.sources && \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm main non-free contrib" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm-updates main non-free contrib" >> /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    libkrb5-dev krb5-config gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 设置容器启动时的命令
#CMD ["python3", "src/start_workflow.py"]