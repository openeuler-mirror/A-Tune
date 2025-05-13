from pydantic import BaseModel
from abc import abstractmethod
from typing import Dict, List, Any, Tuple
from src.utils.shell_execute import remote_execute
from src.utils.llm import get_llm_response
import yaml
import logging
import os
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OptimizerArgs(BaseModel):
    bottle_neck: str = ""
    application: str = ""
    system_report: str = ""
    host_ip: str = ""
    host_port: int = 22
    host_user: str = "root"
    host_password: str = ""
    # ？统一配置文件
    target_config_path: str = ""
    
class BaseOptimizer:
    def __init__(self, **kwargs):
        self.args = OptimizerArgs(**kwargs)
    
    # 写死的命令->执行->保证执行不出错
    # llm生成的脚本->建议
    @abstractmethod
    def think(
        self,
        history: List
    ) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def get_bash_script(self, **kwargs) -> str:
        pass

    # 若执行失败，则需要根据报错信息进行修复(todo)
    def act(
        self, 
        is_execute: bool,
        plan: str
    ) -> bool:
        if not is_execute:
            return is_execute
        try:
            # 将脚本内容写入临时文件
            with open('temp_script.sh', 'w') as file:
                file.write(plan)
            
            # 使脚本文件可执行
            chomd_res = remote_execute(cmd='chmod +x temp_script.sh',host_ip=self.args.host_ip, host_port=self.args.host_port, host_user=self.args.host_user, host_password=self.args.host_password)
            
            # 执行脚本
            script_res = remote_execute(cmd='./temp_script.sh',host_ip=self.args.host_ip, host_port=self.args.host_port, host_user=self.args.host_user, host_password=self.args.host_password)
        except Exception as e:
            print("执行优化脚本时发生错误：", e)
            return not is_execute
        finally:
            # 清理临时文件
            remove_res = remote_execute(cmd='rm temp_script.sh',host_ip=self.args.host_ip, host_port=self.args.host_port, host_user=self.args.host_user, host_password=self.args.host_password)
            return is_execute
    
    # 如果plan是建议，则通过人的反馈获取优化结果，需要与人交互
    # 如果plan是执行，则自动化获取优化结果（需要配置获取优化结果的方法），不需要与人交互
    # 返回值是观察结果
    def observe(
        self,
        is_execute: bool,
        plan: str
    ) -> Dict:
        if not is_execute:
            human_response = self.get_human_response(plan=plan)
            prompt = f"""
            # CONTEXT # 
            以下内容是用户基于调优结果的反馈: 
            {human_response}

            # OBJECTIVE #
            请根据以上信息,判断用户的性能优化目标是否达到。

            # STYLE #
            你是一个专业的系统运维专家,你只用回答True或False

            # Tone #
            你应该尽可能秉承严肃、认真、严谨的态度

            # AUDIENCE #
            你的答案将会是其他系统运维专家的重要参考意见，请认真思考后给出你的答案。

            # RESPONSE FORMAT #
            请回答True或False,不要有多余文字。

            """
            if "true" in get_llm_response(prompt=prompt).lower():
                return {
                    "isfinished": True,
                    "reason": human_response
                }
            else:
                return {
                    "isfinished": False,
                    "reason": human_response
                }
        isfinished, response = self.get_optimize_result(config_path=self.args.target_config_path)
        if isfinished:
            return {
                "isfinished": True,
                "reason": response
            }
        else:
            return {
                "isfinished": False,
                "reason": response
            }

    # 从配置文件中获取如何得到优化结果的方法（todo）
    # 配置文件需要写明如何获得优化结果、优化结果如何判断是否满足用户需求（最好是公式，仿照A-Tune）
    def get_optimize_result(
        self,
        config_path: str
    ) -> Tuple[bool, str]:
        pass
        
    # fake human feedback tmp(todo)
    def get_human_response(
        self,
        plan: str
    ) -> str:
        ask_human = f"here is my advice: {plan}, please try this plan and let me know how it works out. You need to tell me if the tuning plan meet your requirement. if not, the more detailed information you provide, the better it helps me make a improvement."
        human_response = "yeh, it works out, this solution has already taken effect and met my goals."
        return human_response
    
    def get_tuning_config(
        self,
    ) -> Dict[str, Any]:
        current_file_path = os.path.abspath(__file__)
        current_dir_path = os.path.dirname(current_file_path)
        config_file = os.path.join(current_dir_path, '..', '..', 'config', 'optimize_config.yaml')
        try:
            with open(config_file, "r") as f:
                tuning_config = yaml.safe_load(f)
            return tuning_config
        except Exception as e:
            logging.error(f"Failed to parse optimize_config.yaml: {e}")

    # 诊断的loop无需借助优化的结果，maybe <= 3(todo)
    def run(self) -> Any: 
        isfinished = False
        rounds = 1
        record = []
        while not isfinished:
            is_execute, optimization_plan = self.think(history=record)
            is_execute = self.act(is_execute=is_execute, plan=optimization_plan)
            optimization_feedback = self.observe(is_execute=is_execute, plan=optimization_plan)
            isfinished = optimization_feedback["isfinished"]
            if isfinished:
                record.append(f"in '{rounds}'th round, the optimization plan is '{optimization_plan}', and the tuning task has been finished, the reason is: '{optimization_feedback['reason']}'")
                logging.info(f"in '{rounds}'th round, the optimization plan is '{optimization_plan}', and the tuning task has been finished, the reason is: '{optimization_feedback['reason']}'")
            else:
                record.append(f"in '{rounds}'th round, the optimization plan is '{optimization_plan}', and the tuning task has not been finished, the reason is: '{optimization_feedback['reason']}'")
                logging.info(f"in '{rounds}'th round, the optimization plan is '{optimization_plan}', and the tuning task has not been finished, the reason is: '{optimization_feedback['reason']}'")
            rounds += 1
            if rounds > 5:
                break
        return optimization_plan, isfinished, optimization_feedback["reason"]
    