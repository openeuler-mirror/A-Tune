import json
import logging
import os
from typing import List, Tuple

from src.utils.rag.knob_rag import KnobRag
from .base_optimizer import BaseOptimizer
from ..utils.constant import KNOB_RAG_CONFIG_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CORE_CPU_KNOBS = [
    "kernel.numa_balancing",
    "kernel.sched_autogroup_enabled",
    "kernel.sched_wakeup_granularity_ns",
    "kernel.sched_min_granularity"
]
COER_MEMORY_KNOBS = []
CORE_DISK_KNOBS = []
CORE_NETWORK_KNOBS = []
CORE_MYSQL_KNOBS = [
    "mysql.innodb_thread_concurrency",
    "mysql.innodb_lru_scan_depth",
    "mysql.innodb_flush_log_at_trx_commit",
    "mysql.innodb_spin_wait_delay",
    "mysql.innodb_log_buffer_size",
    "mysql.sync_binlog",
    "mysql.innodb_sync_spin_loops",
    "mysql.innodb_write_io_threads",
    "mysql.innodb_read_io_threads",
    "mysql.innodb_purge_threads",
    "mysql.innodb_buffer_pool_instances",
]
CORE_NGINX_KNOBS = []
CORE_REDIS_KNOBS = []


class KnobOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # 根据有无history区分静态调优和动态调优？
    # 基于动态调优的待实现（todo）
    # 基于历史的重新推荐，可以提炼成一个函数
    # 当瓶颈为none时，怎么处理？是否应该不执行优化？
    def think(
            self,
            history: List
    ) -> Tuple[bool, str]:
        tuning_config = self.get_tuning_config()
        if tuning_config["knob_tuning"] == "static":
            if history == []:
                core_system_knob = self.get_core_system_knob()
                core_app_knob = self.get_core_app_knob()
                current_file_path = os.path.abspath(__file__)
                current_dir_path = os.path.dirname(current_file_path)
                rag_config_path = os.path.join(current_dir_path, '..', '..', 'config', 'knob_rag_config.json')
                if not os.path.exists(rag_config_path) or not os.path.isfile(rag_config_path):
                    rag_config_path = KNOB_RAG_CONFIG_PATH
                rag = KnobRag(config_path=rag_config_path, bottle_neck=self.args.bottle_neck,
                              application=self.args.application, system_report=self.args.system_report)
                knobs = rag.run()
                knobs.extend([knob for knob in core_system_knob if knob not in knobs])
                # todo 当用户输入mysql时，但mysql实际没有运行，则其实不应该把这些参数进行添加。
                knobs.extend([knob for knob in core_app_knob if knob not in knobs])

                set_knob_config_path = os.path.join(current_dir_path, 'set_knob_cmd.jsonl')
                set_knob_cmd = {}
                with open(set_knob_config_path, "r", encoding="utf-8") as f:
                    for line in f.readlines():
                        set_knob_cmd = set_knob_cmd | json.loads(line)
                cmd_list = []
                for knob in knobs:
                    if knob in set_knob_cmd:
                        cmd_list.append(set_knob_cmd[knob])
                return False, self.get_bash_script(cmd_list)
            else:
                pass
        elif tuning_config["knob_tuning"] == "dynamic":
            pass
        else:
            # 异常处理（todo）
            pass

    def get_bash_script(
            self,
            cmd_list: List
    ) -> str:
        # 脚本内容的开头部分
        script_header = (
            "#!/bin/bash\n\n"
            "echo 'starting set parameters value...'\n"
        )

        # 将命令列表转换为脚本中的行
        commands_str = "\n".join(cmd_list) + "\n"

        # 脚本内容的结尾部分
        script_footer = (
            "\necho 'set parameters value done!'\n"
        )

        script_content = script_header + commands_str + script_footer
        return script_content

    def get_core_system_knob(
            self,
    ) -> List[str]:
        if self.args.bottle_neck.upper() == "CPU":
            return CORE_CPU_KNOBS
        elif self.args.bottle_neck.upper() == "MEMORY":
            return COER_MEMORY_KNOBS
        elif self.args.bottle_neck.upper() == "DISK":
            return CORE_DISK_KNOBS
        elif self.args.bottle_neck.upper() == "NETWORK":
            return CORE_NETWORK_KNOBS
        else:
            return []

    def get_core_app_knob(
            self,
    ) -> List[str]:
        if not self.args.application:
            return []
        if self.args.application.upper() == "MYSQL":
            return CORE_MYSQL_KNOBS
        elif self.args.application.upper() == "NGINX":
            return CORE_NGINX_KNOBS
        elif self.args.application.upper() == "REDIS":
            return CORE_REDIS_KNOBS
        else:
            return []
