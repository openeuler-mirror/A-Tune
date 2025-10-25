from src.utils.prompt_manager import StringRepository, StringItem
from src.utils.config.global_config import DEFAULT_CONFIG_PATH
prompt_manager = StringRepository(store_path=DEFAULT_CONFIG_PATH + "/strings.yaml", defaults_path=DEFAULT_CONFIG_PATH + "/defaults.yaml")