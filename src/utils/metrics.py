from enum import Enum


class PerformanceMetric(Enum):
    QPS = "QPS：每秒查询请求数（Queries Per Second），单位：次/秒"
    RT = "RT：响应时间（Response Time），即从请求发出到收到响应的时间，单位：毫秒"
    THROUGHPUT = "吞吐量：系统在单位时间内处理的请求数量或数据量，单位：请求数/秒 或 字节/秒"

# 示例使用
if __name__ == "__main__":
    for metric in PerformanceMetric:
        print(metric.value)
        print("-" * 50)
