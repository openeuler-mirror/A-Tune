import logging
import json
import time

from src.performance_optimizer.param_recommender import ParamRecommender
from src.performance_optimizer.param_knowledge import ParamKnowledge
from src.performance_test.pressure_test import wait_for_pressure_test
from src.utils.config.app_config import AppInterface
from src.utils.shell_execute import SshClient
from src.utils.snapshot import load_snapshot, save_snapshot

class ParamOptimizer:

    def __init__(
            self,
            service_name: str,
            slo_goal: float,
            analysis_report: str,
            static_profile: str,
            ssh_client: SshClient,
            slo_calc_callback: callable = None,
            max_iterations: int = 10,
            need_restart_application: bool = False,
            pressure_test_mode: bool = False,
            tune_system_param: bool = False,
            tune_app_param: bool = True,
            need_recover_cluster: bool = False,
            benchmark_timeout: int = 3600,
            param_save_path: str = ""
    ):
        self.service_name = service_name
        self.analysis_report = analysis_report
        self.static_profile = static_profile
        self.ssh_client = ssh_client
        self.pressure_test_mode = pressure_test_mode
        self.max_iterations = max_iterations
        # 计算slo指标提升方式的回调函数，输入是benchmark返回的性能指标，输出是业务性能提升比例
        self.slo_calc_callback = None
        # 业务预期指标提升的目标
        self.slo_goal = slo_goal
        # 可调参数知识库，用于给大模型描述应用参数背景知识
        self.param_knowledge = ParamKnowledge(
            ssh_client=ssh_client,
            tune_system_param=tune_system_param,
            tune_app_param=tune_app_param
        )
        self.all_params = self.param_knowledge.get_params(service_name)
        self.params_set, self.current_params = self.param_knowledge.describe_param_background_knob(
            service_name, self.all_params
        )
        # 应用接口，包括应用参数下发、benchmark执行等操作
        self.app_interface = AppInterface(ssh_client).get(service_name)
        self.system_interface = AppInterface(ssh_client).system
        self.need_restart_application = need_restart_application
        self.need_recover_cluster = need_recover_cluster
        self.param_recommender = ParamRecommender(
            service_name=service_name,
            slo_goal=slo_goal,
            performance_metric=self.app_interface.performance_metric,
            static_profile=static_profile,
            performance_analysis_report=analysis_report,
            ssh_client=ssh_client,
            all_params=self.all_params,
            params_set=self.params_set
        )
        self.first_restart_save = True
        self.benchmark_timeout=benchmark_timeout
        self.param_save_path = param_save_path

    def calc_improve_rate(self, baseline, benchmark_result, symbol):
        if baseline is None or abs(baseline) < 1e-9:
            return 0.0
        return symbol * (benchmark_result - baseline) / baseline

    def reached_goal(self, baseline, benchmark_result, symbol):
        if self.calc_improve_rate(baseline, benchmark_result, symbol) >= self.slo_goal:
            return True
        return False

    def benchmark(self):
        logging.info(f"🔄 start to verify benchmark performance of {self.service_name}...")
        result = self.app_interface.benchmark()
        if result.status_code == 0 and result.output:
            try:
                perf_value = float(result.output)
                logging.info(f"benchmark success, performance value: {perf_value}")
                return perf_value
            except Exception as e:
                logging.warning(f"benchmark failed, the result is: {result.output}")
                return None
        else:
            logging.warning(f"benchmark execute failed: ret code {result.status_code} {result.err_msg}")
            return None

    def apply_params(self, recommend_params):
        for param_name, param_value in recommend_params.items():
            # 跳过空参数值
            if param_value == "" or param_value is None:
                continue
            apply_result = self.app_interface.set_param(param_name, param_value)
            if apply_result.status_code == 0:
                logging.info(f"set param {param_name} to {param_value}")
            else:
                logging.info(f"set param {param_name} failed, reason: {apply_result.err_msg}")

    def restart_application(self):
        logging.info(f"🔄 restarting the application of {self.service_name} ...")
        stop_result = self.app_interface.stop_workload()
        if stop_result.status_code != 0:
            logging.warning(f"failed to stop application because {stop_result.err_msg}")
        start_result = self.app_interface.start_workload()
        if start_result.status_code != 0:
            logging.warning(f"failed to start application because {start_result.err_msg}")
            return False
        logging.info("🔄 application restarted successfully")
        return True

    def recover_cluster(self):
        logging.info("🔄 restoring the cluster ...")
        recover_result = self.app_interface.recover_workload()
        if recover_result.status_code != 0:
            raise RuntimeError(
                f"failed to recover cluster because {recover_result.err_msg}"
            )

    def save_restart_params_to_script(self, recommend_params, script_path, batch_id):
        """
        将推荐参数保存到脚本中（仅在调优过程中需要重置参数的情况使用）
        """

        commands = []
        for param_name, param_value in recommend_params.items():
            cmd = self.app_interface.generate_set_command(param_name, param_value)
            if cmd:
                commands.append(cmd)

        if not commands:
            logging.info(f"No parameters require restart to take effect in round {batch_id}; skipping script writing.")
            return

        # 构建要追加的内容
        batch_header = f"\n# Batch {batch_id} - Parameters effective after restart\n"
        content = batch_header + '\n'.join(commands)

        if self.first_restart_save:
            init_cmd = f"echo '#!/bin/bash' > {script_path}"
            self.ssh_client.run_cmd(init_cmd)
            self.first_restart_save = False
            logging.info(f"first-time creation of restart parameter script: {script_path}")

        append_cmd = f"cat << 'EOF' >> {script_path}\n{content}\nEOF"
        self.ssh_client.run_cmd(append_cmd)

        logging.info(f"{len(commands)} parameters have been written to the restart script: {script_path}")

    def save_best_params(self, params):
        if self.param_save_path:
            with open(self.param_save_path, 'w', encoding='utf-8') as f:
                json.dump(params, f, ensure_ascii=False, indent=4)
            logging.info(f"[ParamOptimizer] The recommended parameters have beed saved to {self.param_save_path}")
        else:
            logging.warning(f"[ParamOptimizer] The recommended parameter save path is not set")

    def run(self):
        # 运行benchmark，摸底参数性能指标
        if self.pressure_test_mode:
            logging.info(f"[ParamOptimizer] waiting for pressure test finished ...")
            pressure_test_result = wait_for_pressure_test(timeout=self.benchmark_timeout)

            if pressure_test_result.status_code != 0:
                raise RuntimeError(
                    f"[ParamOptimizer] failed to run pressure test, err msg is {pressure_test_result.err_msg}"
                )

            baseline = float(pressure_test_result.output)
            logging.info(
                f"[ParamOptimizer] pressure test finished, baseline is {baseline}"
            )
        else:
            baseline = self.benchmark()
        # 保存每轮调优的结果，反思调优目标是否达到
        historys = {
            "best_result": {},
            "worst_result": {},
            "previous_result": {}
        }
        best_result = baseline
        worst_result = baseline
        curr_recommend_params = {}
        best_recommend_params = {}
        is_positive = True
        symbol = self.app_interface.get_calculate_type()
        logging.info(
            f"[{0}/{self.max_iterations}] performance baseline of {self.service_name} is: {baseline}"
        )

        for i in range(self.max_iterations):
            # 未达成目标的情况下，根据调优结果与历史最优的参数，执行参数调优推荐，给出参数名和参数值
            recommend_params = self.param_recommender.run(history_result=historys, is_positive=is_positive)

            # 设置参数生效
            self.apply_params(recommend_params)
            if self.need_restart_application:
                restart_success = self.restart_application()
                if not restart_success:
                    logging.warning(f"[{i + 1}/{self.max_iterations}] application restart failed due to invalid parameters, reverting to round {i} configuration...")
                    historys["previous_result"] = {"previous_performance": "application restart, because param is invalid", "recommend_param": recommend_params}
                    self.apply_params(self.current_params)
                    restart_success = self.restart_application()
                    logging.warning(f"round {i} configuration recovery {'succeeded' if restart_success else 'failed'}")
                    continue
                # 重启后等待2秒，防止压测启动过快
                time.sleep(2)

            # 执行benchmark，反馈调优结果
            performance_result = self.benchmark()
            if self.need_recover_cluster:
                # 保存在一个/tmp目录下的脚本中
                script_path = '/tmp/euler-copilot-params.sh'
                self.save_restart_params_to_script(recommend_params, script_path, i + 1)
                self.recover_cluster()
            if performance_result is None:
                historys["previous_result"] = {"previous_performance": "benchmark failed, because param is invalid.", "recommend_param": recommend_params}
                self.apply_params(self.current_params)
                restart_success = True
                if self.need_restart_application:
                    restart_success = self.restart_application()
                logging.warning(f"[{i + 1}/{self.max_iterations}] benchmark failed, because param is invalid. \
                                    Restoring configuration for round {i}, restoration successful: {restart_success}")
                continue
            self.current_params.update(recommend_params)
            curr_recommend_params.update(recommend_params)

            if performance_result * symbol < baseline * symbol:
                is_positive = False
            else:
                is_positive = True

            if performance_result * symbol > best_result * symbol:
                best_result = performance_result
                best_recommend_params = dict(curr_recommend_params)
                best_history = {"best_performance": performance_result, "recommend_param": recommend_params}
                historys["best_result"] = best_history
                self.save_best_params(recommend_params)

            if performance_result * symbol < worst_result * symbol:
                worst_result = performance_result
                worst_history = {"worst_performance": performance_result, "recommend_param": recommend_params}
                historys["worst_result"] = worst_history

            historys["previous_result"] = {"previous_performance": performance_result, "recommend_param": recommend_params}

            ratio = self.calc_improve_rate(baseline, performance_result, symbol)

            logging.info(
                f"[{i + 1}/{self.max_iterations}] performance baseline of {self.service_name} is {baseline}, best result: {best_result}, this round result: {performance_result if performance_result is not None else '-'}, performance improvement: {ratio:.2%}"
            )

            # 达到预期效果，则退出循环
            if self.reached_goal(baseline, performance_result, symbol):
                break

        logging.info(
            f"optimization completed, {'reached' if self.reached_goal(baseline, best_result, symbol) else 'did not reach'} expected goal"
        )

        # 配置最优参数
        logging.info(f"configure best performance param: ")
        self.apply_params(best_recommend_params)
        if self.need_restart_application:
            restart_success = self.restart_application()
            if restart_success:
                logging.info(f"application restart completed")
            else:
                logging.error(f"failed to restart the application.")

