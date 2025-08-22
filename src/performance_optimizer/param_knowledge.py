# 知识库加载一次即可
import threading
import logging
from typing import Iterable
from tqdm import tqdm
from src.utils.config.global_config import param_config
from src.utils.config.app_config import AppInterface
from src.utils.shell_execute import SshClient


class ParamKnowledge:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, ssh_client: SshClient):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ParamKnowledge, cls).__new__(cls)
                    cls._instance.param_config = param_config
                    cls._instance.ssh_client = ssh_client  # 保存 ssh_client
        return cls._instance

    def __init__(self, ssh_client: SshClient):
        logging.info(f"[ParamKnowledge] initializing param knowledge base ...")
        # 防止重复初始化
        if not hasattr(self, "ssh_client"):
            self.ssh_client = ssh_client

    def get_params(self, app_name, enable_system_tuning):
        app_params = self.param_config.get(app_name, {})
        if not app_params:
            raise ValueError(f"App '{app_name}' not found in param_config.")

        # 只有在启用系统调优时才加载并检查系统参数
        if enable_system_tuning:
            system_params = self.param_config.get("system", {})
            duplicate_keys = set(system_params) & set(app_params)
            if duplicate_keys:
                raise RuntimeError(
                    f"Duplicate keys ({duplicate_keys}) detected between system and app '{app_name}'."
                )
            return list(system_params.keys()) + list(app_params.keys())
        else:
            return list(app_params.keys())

    def describe_param_background_knob(self, app_name: str, params: Iterable):
        logging.info(f"[ParamKnowledge] building param knowledge base ...")
        params_describe_list = []
        app_params = self.param_config.get(app_name.lower())
        system_params = self.param_config.get("system")
        app = AppInterface(self.ssh_client).get(app_name)
        for param_name in tqdm(params):
            item = (
                app_params.get(param_name)
                if param_name in app_params
                else system_params.get(param_name)
            )
            if not item:
                print(f"param {param_name} not in app param or system param")
                continue
            # 1.描述参数范围
            if item["range"]:
                if item["type"] == "discrete":
                    param_range = "、".join(list(map(str, item["range"])))
                else:
                    param_range = f"从{item['range'][0]}到{item['range'][1]}"
            else:
                param_range = None
            # 2.当前环境取值
            param_result = app.get_param(param_name=param_name)
            param_env_value = (
                param_result.output if param_result.status_code == 0 else "默认值"
            )
            params_describe_list.append(
                f"{param_name}:{item['desc']},参数数据类型为：{item['dtype']}，参数的取值范围是：{param_range}, 当前环境取值为：{param_env_value}"
            )
        logging.info(f"[ParamKnowledge] initialize param knowledge base finished!")
        return params_describe_list


if __name__ == "__main__":

    class Result:
        def __init__(self, status_code, output):
            self.status_code = status_code
            self.output = output

    class SshClient:
        def __init__(self):
            pass

        def run_cmd(self, cmd):
            return Result(0, "12")

    ssh_client = SshClient()
    param_knowledge = ParamKnowledge(ssh_client)
    res = param_knowledge.describe_param_background_knob(
        "mysql", ["innodb_adaptive_flushing"]
    )
    print(res)
