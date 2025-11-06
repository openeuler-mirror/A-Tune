import logging
from src.config import config
from src.utils.common import display_banner

logging.getLogger("paramiko.transport").propagate = False
display_banner()

level_name = str(config.__getitem__("log_level") or "INFO").upper()
logging.basicConfig(
    level=getattr(logging, level_name, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
