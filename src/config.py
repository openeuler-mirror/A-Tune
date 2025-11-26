import os
import yaml

from src.utils.constant import ENV_CONFIG_PATH


class Config:
    config: dict

    def __init__(self):
        self.config_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "config", ".env.yaml")
        )
        if not os.path.exists(self.config_file) or not os.path.isfile(self.config_file):
            self.config_file = ENV_CONFIG_PATH

        self.load()

    def load(self):
        with open(self.config_file, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file) or {}

    def reload(self):
        self.load()

    def __getitem__(self, key):
        if key in self.config:
            return self.config[key]
        else:
            return None


config = Config()
