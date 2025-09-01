import os
import re
from enum import Enum
from string import Template
from dataclasses import dataclass, asdict, field

from src.utils.constant import SCRIPTS_PATH
from src.utils.shell_execute import SshClient
from src.utils.config.global_config import env_config, param_config
from src.utils.metrics import PerformanceMetric

# 某个app需要注册私有的模板方法，可存在这里
REGISTERED_TEMPLATE = {}


class ExecuteMode(Enum):
    REMOTE = "remote"
    LOCAL = "local"


ALL_EXECUTE_MODES = "|".join(mode.value for mode in ExecuteMode)
EXECUTE_MODE_PATTERN = re.compile(rf"^\$EXECUTE_MODE:\s*({ALL_EXECUTE_MODES})?\s*(.*)")


def default_scripts_dir():
    scripts_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts")
    )

    # 检查原始目录是否存在
    if os.path.exists(scripts_dir) and os.path.isdir(scripts_dir):
        return scripts_dir
    else:
        return SCRIPTS_PATH


def app_template(key):
    """
    类修饰器，重写AppInterface方法后，通过该接口注册模板方法
    用于某些特殊的应用与默认流程不同，需要重载处理流程的情况

    下面给一个重写mysql执行benchmark的实例：
    @app_template("mysql") # 使用该注解之后就默认会使用该自定义方法处理benchmark的流程
    class MysqlTemplate(AppTemplate):
        def benchmark(self, ssh_client):
            exec_result = ssh_client.run_cmd(self.benchmark)
            if exec_result.status_code == 0:
                return exec_result.result
            else:
                return 0
    """

    def decorator(cls):
        REGISTERED_TEMPLATE[key] = cls
        return cls

    return decorator


# 根据kwargs填充shell命令模板，生成可用的shell命令
def shell_template(template_str, **kwargs):
    processed_str = re.sub(r"\$(\d+)", r"$$\1", template_str)
    template = Template(processed_str)
    processed_template = template.substitute(**kwargs)
    postprocessed_str = re.sub(r"\$\$(\d+)", r"$\1", processed_template)
    return postprocessed_str


@dataclass
class AppMetaConfig:
    app_name: str
    user: str
    port: str
    password: str
    config_file: str
    host_ip: str
    host_port: int
    SCRIPTS_DIR: str = field(default_factory=default_scripts_dir)


class AppTemplate:
    def __init__(
            self,
            ssh_client: SshClient,
            app_name: str = "",
            user: str = "",
            port: str = "",
            password: str = "",
            config_file: str = "",
            get_param_template: str = "",
            set_param_template: str = "",
            start_workload: str = "",
            stop_workload: str = "",
            recover_workload: str = "",
            benchmark: str = "",
            performance_metric: str = ""
    ):
        # 应用的基本配置，填充模板可能会用到
        self.meta_data = asdict(
            AppMetaConfig(
                app_name=app_name,
                user=user,
                port=port,
                password=password,
                config_file=config_file,
                host_ip=ssh_client.host_ip,
                host_port=ssh_client.host_port,
            )
        )
        self.app_params = param_config.get(app_name)
        self.system_params = param_config.get("system")
        self.ssh_client = ssh_client
        self.get_param_template = get_param_template
        self.set_param_template = set_param_template
        self.start_workload_cmd = start_workload
        self.stop_workload_cmd = stop_workload
        self.recover_workload_cmd = recover_workload
        self.benchmark_cmd = benchmark
        if app_name != "system":
            try:
                self.performance_metric = PerformanceMetric[performance_metric]
            except KeyError:
                supported_metrics = list(PerformanceMetric.__members__.keys())
                raise KeyError(
                    f"Performance metric '{performance_metric}' is not supported. "
                    f"Supported metrics are: {supported_metrics}"
                )
        else:
            self.performance_metric = PerformanceMetric["QPS"]
        self.mode_map = {
            ExecuteMode.REMOTE: ssh_client.run_cmd,
            ExecuteMode.LOCAL: ssh_client.run_local_cmd,
        }

    def extract_mode(self, cmd):
        match = EXECUTE_MODE_PATTERN.match(cmd)
        if match:
            mode_str = match.group(1)
            remaining_string = match.group(2).strip()
            mode = ExecuteMode.REMOTE if mode_str is None else ExecuteMode(mode_str)
            return self.mode_map[mode], remaining_string
        else:
            return self.mode_map[ExecuteMode.REMOTE], cmd

    def get_param(self, param_name):
        if param_name in self.system_params:
            get_param_template = self.system_params[param_name]["get"]
        else:
            get_param_template = self.get_param_template
        if not self.get_param_template:
            return None
        run_cmd_func, cmd = self.extract_mode(get_param_template)
        cmd = shell_template(
            cmd,
            param_name=param_name,
            **self.meta_data,
        )
        return run_cmd_func(cmd)

    def set_param(self, param_name, param_value):
        if param_name in self.system_params:
            set_param_template = self.system_params[param_name]["set"]
        else:
            set_param_template = self.set_param_template
        if not self.set_param_template:
            return None
        run_cmd_func, cmd = self.extract_mode(set_param_template)
        cmd = shell_template(
            cmd,
            param_name=param_name,
            param_value=param_value,
            **self.meta_data,
        )
        return run_cmd_func(cmd)

    def start_workload(self):
        if not self.start_workload_cmd:
            return None
        run_cmd_func, cmd = self.extract_mode(self.start_workload_cmd)
        cmd = shell_template(
            cmd,
            **self.meta_data,
        )
        return run_cmd_func(cmd)

    def stop_workload(self):
        if not self.stop_workload_cmd:
            return None
        run_cmd_func, cmd = self.extract_mode(self.stop_workload_cmd)
        cmd = shell_template(
            cmd,
            **self.meta_data,
        )
        return run_cmd_func(cmd)

    def recover_workload(self):
        if not self.recover_workload_cmd:
            return None
        run_cmd_func, cmd = self.extract_mode(self.recover_workload_cmd)
        cmd = shell_template(
            cmd,
            **self.meta_data,
        )
        return run_cmd_func(cmd)

    def generate_set_command(self, param_name, param_value):
        if param_name in self.system_params:
            set_param_template = self.system_params[param_name]["set"]
        else:
            set_param_template = self.set_param_template
        if not self.set_param_template:
            return None
        _, cmd = self.extract_mode(set_param_template)

        formatted_cmd = shell_template(
            cmd,
            param_name=param_name,
            param_value=param_value,
            **self.meta_data,
        )
        return formatted_cmd

    def benchmark(self):
        if not self.benchmark_cmd:
            return None
        run_cmd_func, cmd = self.extract_mode(self.benchmark_cmd)
        cmd = shell_template(
            cmd,
            **self.meta_data,
        )
        return run_cmd_func(cmd)

    def get_calculate_type(self):
        if self.performance_metric == PerformanceMetric.DURATION or self.performance_metric == PerformanceMetric.RT:
            # 耗时和响应时间等越小越好
            return -1
        else:
            # QPS 和吞吐量等越大越好
            return 1


# 将配置文件反序列化成可执行的函数，例如：
# 下面就是一个实例化mysql应用
# application = AppInterface()
# application.mysql.start_workload()
class AppInterface:
    _instance = None
    _initialized = False

    def __new__(cls, ssh_client: SshClient):
        if cls._instance is None:
            cls._instance = super(AppInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self, ssh_client: SshClient):
        # 防止重复初始化
        if not getattr(self, "_initialized", False):
            self._config = env_config.get("app_config")
            self._instances = {}
            self.ssh_client = ssh_client  # 保存 ssh_client
            self._initialize_instances()
            self.__class__._initialized = True

    def _initialize_instances(self):
        for app_name, app_config in self._config.items():
            # 优先使用 REGISTERED_TEMPLATE 中的类
            cls = REGISTERED_TEMPLATE.get(app_name, AppTemplate)
            self._instances[app_name] = cls(
                app_name=app_name, ssh_client=self.ssh_client, **app_config
            )

    def __contains__(self, param_name):
        pass

    def __getattr__(self, item):
        return self.get(item)

    def get(self, item):
        if item in self._instances:
            return self._instances[item]
        raise AttributeError(f"'AppInterface' object has no attribute '{item}'")


if __name__ == "__main__":
    class SshClient:
        def __init__(self):
            pass

        def run_cmd(self, cmd):
            print(cmd)


    ssh_client = SshClient()
    app_interface = AppInterface(ssh_client)
    app = app_interface.mysql
    sys = app_interface.system

    app.get_param("hello")
    app.set_param("hello", 1)
    app.start_workload()
    app.stop_workload()
    app.benchmark()

    sys.get_param("aaa")
    sys.set_param("bbb", 2)
