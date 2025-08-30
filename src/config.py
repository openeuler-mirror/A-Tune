import os
import yaml

from src.utils.constant import ENV_CONFIG_PATH


class Config:
    config: dict

    def __init__(self):
        if os.getenv("CONFIG"):
            config_file = os.getenv("CONFIG")
        else:
            config_file = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "config", ".env.yaml")
            )
            if not os.path.exists(config_file) or not os.path.isfile(config_file):
                config_file = ENV_CONFIG_PATH

        with open(config_file, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)
        if os.getenv("PROD"):
            os.remove(config_file)

    def __getitem__(self, key):
        if key in self.config:
            return self.config[key]
        else:
            return None


config = Config()
