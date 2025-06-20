import logging
from src.utils.common import display_banner

logging.getLogger("paramiko.transport").propagate = False
display_banner()
