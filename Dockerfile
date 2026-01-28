# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# Optimized: Multi-stage build and image size reduction

# ============================================================================
# Stage 1: Builder - Install build dependencies and prepare environment
# ============================================================================
FROM python:3.11.6-slim AS builder

# Configure APT mirror for faster downloads (Alibaba Cloud)
RUN echo > /etc/apt/sources.list.d/debian.sources && \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm main non-free contrib" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm-updates main non-free contrib" >> /etc/apt/sources.list

# Install build dependencies in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-dev \
        libkrb5-dev \
        krb5-config \
        gcc \
        && \
    # Configure pip mirror for faster downloads
    pip install --upgrade pip setuptools wheel && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    # Clean up apt cache
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set working directory
WORKDIR /build

# Copy dependency files first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy source code
COPY . .

# ============================================================================
# Stage 2: Runtime - Minimal runtime environment
# ============================================================================
FROM python:3.11.6-slim

# Set labels
LABEL maintainer="A-Tune Team" \
      description="Euler Copilot Tune - AI-based performance tuning service" \
      version="1.0"

# Configure APT mirror
RUN echo > /etc/apt/sources.list.d/debian.sources && \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm main non-free contrib" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm-updates main non-free contrib" >> /etc/apt/sources.list

# Install only runtime dependencies (no build tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ssh \
        busybox \
        krb5-user \
        && \
    # Clean up cache
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Configure pip mirror
RUN pip install --upgrade pip && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    rm -rf /root/.cache/pip

# Set working directory
WORKDIR /euler-copilot-tune

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code (only necessary files)
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY service/ ./service/
COPY setup.py .
COPY requirements.txt .

# Make sure scripts in .local/bin are usable
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/euler-copilot-tune:$PYTHONPATH

# Set proper permissions
RUN chmod -R 755 /euler-copilot-tune/scripts 2>/dev/null || true

# Use non-root user for security (optional, can be enabled if needed)
# RUN useradd -m -u 1000 appuser && \
#     chown -R appuser:appuser /euler-copilot-tune
# USER appuser

# Expose default port (adjust if needed)
# EXPOSE 8000

# Set container startup command
CMD ["python3", "src/start_workflow.py"]
