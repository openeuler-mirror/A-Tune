import os
import yaml


class Config:
    config: dict

    def __init__(self):
        if os.getenv("CONFIG"):
            config_file = os.getenv("CONFIG")
        else:
            config_file = "./config/.env.yaml"
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