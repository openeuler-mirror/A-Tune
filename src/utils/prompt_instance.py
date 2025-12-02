from src.utils.prompt_manager import StringRepository, StringItem
from src.utils.config.global_config import DEFAULT_CONFIG_PATH
from src.utils.common import language
default = "/defaults"
if language() == "zh":
    default += "_" + language()
default += ".yaml"
prompt_manager = StringRepository(store_path=DEFAULT_CONFIG_PATH + "/strings.yaml", defaults_path=DEFAULT_CONFIG_PATH + default)