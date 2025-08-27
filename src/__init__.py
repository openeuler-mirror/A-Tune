import logging
from src.utils.common import display_banner

logging.getLogger("paramiko.transport").propagate = False
display_banner()

logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format="%(asctime)s - %(levelname)s [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s",  # 设置日志格式
    datefmt="%Y-%m-%d %H:%M:%S",  # 设置时间格式
)
