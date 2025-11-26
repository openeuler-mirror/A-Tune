import os
import json
import yaml
import logging
from typing import Any, Optional, Dict, List, Union
from pathlib import Path

from src.utils.constant import CONFIG_PATH, KNOWLEDGE_PATH


class EnvironConfig:
    def __init__(self, config_dir: str):
        """
        初始化配置加载器，读取指定目录下的所有 .json / .yaml / .yml 文件

        :param config_dir: 配置文件所在目录
        """
        self.config_dir = Path(config_dir).resolve()
        if not self.config_dir.exists() or not self.config_dir.is_dir():
            raise FileNotFoundError(f"Config directory not found: {config_dir}")

        self._configs: Dict[str, dict] = {}

        # 加载所有支持的配置文件
        self._load_all_config_files()

    def _load_all_config_files(self):
        for file in self.config_dir.iterdir():
            if file.suffix.lower() in (".json", ".yaml", ".yml"):
                name = file.stem  # 不带扩展名的文件名
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        if file.suffix == ".json":
                            self._configs[name] = json.load(f)
                        else:
                            self._configs[name] = yaml.safe_load(f) or {}
                except Exception as e:
                    logging.warning(f"Failed to load config file: {file.name}, error: {e}")
            # load app params: {KNOWLEDGE_PATH}/{app_name}/v{version}.json
            if os.path.isdir(file):
                app_param_dir = Path(file).resolve()
                app_name = file.name  # 不带扩展名的文件名
                if app_name not in self._configs:
                    self._configs[app_name] = {}
                # load all version json to config dict, key is version, value is loaded json
                for version_param_file in app_param_dir.iterdir():
                    if version_param_file.suffix.lower() == ".json":
                        version = version_param_file.stem  # 不带扩展名的文件名
                        try:
                            with open(version_param_file, "r", encoding="utf-8") as f:
                                self._configs[app_name][version] = json.load(f)
                        except Exception as e:
                            logging.warning(f"Failed to load config file: {version_param_file.name}, error: {e}")

    def get(self, key_path: str, default: Optional[Any] = None) -> Union[Dict, Any]:
        """
        获取配置值，使用点号分隔的路径访问嵌套字段

        :param key_path: 如 "filename" 或 "filename.section.key"
        :param default: 如果找不到返回的默认值
        :return: 配置值或默认值
        """
        keys = key_path.split(".")
        filename = keys[0]

        config = self._configs.get(filename)
        if config is None:
            return default

        if len(keys) == 1:
            return config

        current = config
        for key in keys[1:]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def find_key(self, target_key: str) -> List[str]:
        """
        查找某个 key 在哪些配置文件中作为顶层 key 出现过
        :param target_key: 要查找的 key 名称
        :return: 包含这个 key 的所有文件名列表（不带扩展名）
        """
        result = []
        for filename, config in self._configs.items():
            if isinstance(config, dict) and target_key in config:
                result.append(filename)
        return result


DEFAULT_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "config")
)
if not os.path.exists(DEFAULT_CONFIG_PATH) or not os.path.isdir(DEFAULT_CONFIG_PATH):
    DEFAULT_CONFIG_PATH = CONFIG_PATH

PARAMS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base", "knob_params")
)
if not os.path.exists(PARAMS_PATH) or not os.path.isdir(PARAMS_PATH):
    PARAMS_PATH = os.path.join(KNOWLEDGE_PATH, "knob_params")

env_config = EnvironConfig(DEFAULT_CONFIG_PATH)
param_config = EnvironConfig(PARAMS_PATH)

def init():
    env_app_name = env_config._configs[".env"]["servers"][0]["app"]
    env_app_version = env_config.get(f"app_config.{env_app_name}.version")
    env_app_version = "" if env_app_version is None else env_app_version
    logging.info(f"env {env_app_name} version: {env_app_version}")

    param_versions = list(param_config.get(env_app_name).keys())
    logging.info(f"available {env_app_name} param knowledge versions: {param_versions}")
    
    # 找到相同或更高的版本号
    choosen_param_version = sorted(param_versions)[0]
    for param_version in sorted(param_config.get(env_app_name).keys()):
        if param_version >= env_app_version:
            break
        choosen_param_version = param_version
    logging.info(f"use {env_app_name} param knowledge version: {choosen_param_version}")
    # param_config中仅保留最终选择版本
    param_config._configs[env_app_name] = param_config._configs[env_app_name][choosen_param_version]

init()


if __name__ == "__main__":
    # print(env_config._configs)
    # print(env_config._configs[".env"])
    # print(env_config._configs["app_config"])
    # print(env_config.get("app_config.mysql.version"))
    print(param_config.get("mysql"))