import logging
from src.config import config
from src.utils.common import display_banner

logging.getLogger("paramiko.transport").propagate = False
display_banner()

logging.basicConfig(
    level=getattr(logging, config["log_level"].upper(), logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
