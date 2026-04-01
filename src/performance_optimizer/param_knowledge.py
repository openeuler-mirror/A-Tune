import logging
import threading
from typing import Iterable

from tqdm import tqdm

from src.utils.config.app_config import AppInterface
from src.utils.config.global_config import param_config
from src.utils.shell_execute import SshClient
from src.utils.common import language


class ParamKnowledge:
    def __init__(self,
                 ssh_client: SshClient,
                 tune_system_param: bool = False,
                 tune_app_param: bool = True):
        logging.info(f"[ParamKnowledge] initializing param knowledge base ...")
        self.param_config = param_config
        self.ssh_client = ssh_client
        self.tune_system_param = tune_system_param
        self.tune_app_param = tune_app_param

    def get_params(self, app_name):
        # check 应用和系统参数是否有重名的
        logging.info(f"[ParamKnowledge] checking params ...")
        system_params = set()
        app_params = set()
        all_params = []
        if self.tune_system_param:
            system_params = set(self.param_config.get("system", {}).keys())
            all_params += list(self.param_config.get("system").keys())
        if self.tune_app_param:
            app_params = set(self.param_config.get(app_name, {}).keys())
            all_params += list(self.param_config.get(app_name).keys())
        union_params = system_params & app_params
        if union_params:
            raise RuntimeError(
                f"Duplicate keys ({union_params}) detected between application parameters and system parameters."
            )
        return all_params

    def describe_param_background_knob(self, app_name: str, params: Iterable):
        logging.info(f"[ParamKnowledge] building param knowledge base ...")
        params_describe_list = []
        params_info = {}
        is_zh = (language() == "zh")
        app_params = self.param_config.get(app_name.lower())
        system_params = self.param_config.get("system")
        app = AppInterface(self.ssh_client).get(app_name)
        for param_name in tqdm(params):
            if param_name in app_params:
                item = app_params.get(param_name)
            else:
                item = system_params.get(param_name)
            if not item:
                logging.warning(f"param {param_name} not in app param or system param")
                continue
            # 1.描述参数范围
            if item["range"]:
                if item["type"] == "discrete":
                    if is_zh:
                        param_range = "、".join(list(map(str, item["range"])))
                        param_range = f"参数只允许配置为（{param_range}）里的其中一个"
                    else:
                        param_range = ",".join(list(map(str, item["range"])))
                        param_range = f"the parameter can be set to only one of ({param_range})"
                else:
                    if is_zh:
                        param_range = f"参数可配置的范围为 {item['range'][0]} 到 {item['range'][1]}（{item['range'][0]} 和 {item['range'][1]} 均可配置）"
                    else:
                        param_range = f"the parameter can be set within the range from {item['range'][0]} to {item['range'][1]} ({item['range'][0]} and {item['range'][1]} can both be set)"
            else:
                logging.warning(f"The \"range\" is not configured for param {param_name}")
                continue
            # 2.当前环境取值
            param_result = app.get_param(param_name=param_name)
            param_env_value = (
                param_result.output if param_result.status_code == 0 else item.get("default_value", "the default value of the application")
            )
            param_prompt = ""
            if is_zh:
                param_prompt = f"{param_name}:{item['desc']}, 参数类型为 {item['dtype']} 类型, {param_range}, 当前 {param_name} = {param_env_value}。"
            else:
                param_prompt = f"{param_name}:{item['desc']}, the parameter type is \"{item['dtype']}\", {param_range}, current {param_name} = {param_env_value}."
            params_describe_list.append(param_prompt)
            params_info[param_name] = param_env_value
        logging.info(f"[ParamKnowledge] initialize param knowledge base finished!")
        return params_describe_list, params_info


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
