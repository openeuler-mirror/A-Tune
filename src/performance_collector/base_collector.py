from pydantic import BaseModel
from abc import abstractmethod
from typing import Dict, List, Any
from src.utils.shell_execute import remote_execute

class CollectorArgs(BaseModel):
    cmds: List[str] = []
    host_ip: str = ""
    host_port: int = 22
    host_user: str = "root"
    host_password: str = ""

class BaseCollector:
    def __init__(self, **kwargs):
        # 使用pydantic模型的构造函数来初始化args
        self.args = CollectorArgs(**kwargs)

    def get_cmd_stdout(
        self,
    ) -> Dict:
        # 执行远程命令
        result = {}
        for cmd in self.args.cmds:
            cmd_res = remote_execute(
                cmd=cmd,
                host_ip=self.args.host_ip,
                host_port=self.args.host_port,
                host_user=self.args.host_user,
                host_password=self.args.host_password,
            )
            result = {**result, **cmd_res}
        return result

    @abstractmethod
    def parse_cmd_stdout(self, **kwargs) -> Dict:
        pass

    def default_parse(
        self,
        cmd: str,
        stdout: Any,
    ) -> Dict:
        return {cmd: stdout}
    
    @abstractmethod
    def data_process(self, **kwargs) -> Dict:
        pass

    def run(self) -> Dict:
        # 1. 获取命令执行结果
        cmd_stdout = self.get_cmd_stdout()

        # 2. 解析命令输出
        parsed_data = self.parse_cmd_stdout(cmd_stdout)

        # 3. 处理数据
        processed_data = self.data_process(parsed_data)

        # 4. 返回处理后的数据
        return processed_data
