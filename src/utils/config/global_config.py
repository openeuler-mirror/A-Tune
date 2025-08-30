import os
import json
import yaml
from typing import Any, Optional, Dict, List
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
                    print(
                        f"[Warning] Failed to load config file: {file.name}, error: {e}"
                    )

    def get(self, key_path: str, default: Optional[Any] = None) -> Any:
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
