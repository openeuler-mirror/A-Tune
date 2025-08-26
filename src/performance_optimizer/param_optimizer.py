import logging
from src.utils.shell_execute import SshClient
from src.performance_optimizer.param_recommender import ParamRecommender
from src.utils.metrics import PerformanceMetric
from src.utils.config.app_config import AppInterface
from src.performance_test.pressure_test import wait_for_pressure_test

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ParamOptimizer:

    def __init__(
        self,
        service_name: str,
        slo_goal: float,
        analysis_report: str,
        static_profile: str,
        ssh_client: SshClient,
        slo_calc_callback: callable,
        max_iterations: int = 10,
        need_restart_application: bool = False,
        need_recover_cluster: bool = False,
        pressure_test_mode: bool = False,
        enable_system_tuning: bool = False
    ):
        self.service_name = service_name
        self.analysis_report = analysis_report
        self.static_profile = static_profile
        self.ssh_client = ssh_client
        self.pressure_test_mode = pressure_test_mode
        self.max_iterations = max_iterations
        # 计算slo指标提升方式的回调函数，输入是benchmark返回的性能指标，输出是业务性能提升比例
        self.slo_calc_callback = slo_calc_callback
        # 业务预期指标提升的目标
        self.slo_goal = slo_goal
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
            enable_system_tuning=enable_system_tuning
        )
        self.first_restart_save = True
    def calc_improve_rate(self, baseline, benchmark_result, symbol):
        return self.slo_calc_callback(baseline, benchmark_result, symbol)

    def reached_goal(self, baseline, benchmark_result, symbol):
        if self.calc_improve_rate(baseline, benchmark_result, symbol) >= self.slo_goal:
            return True
        return False

    def benchmark(self):
        print("🔄 正在验证benchmark性能...")
        result = self.app_interface.benchmark()
        if result.status_code == 0:
            return float(result.output)
        else:
            raise RuntimeError(f"failed to execute benchmark because {result.err_msg}")

    def apply_params(self, recommend_params):
        for param_name, param_value in recommend_params.items():
            apply_result = self.app_interface.set_param(param_name, param_value)
            if apply_result.status_code == 0:
                print(f"设置参数{param_name}为{param_value}")
            else:
                print(f"设置参数{param_name}失败，原因是：{apply_result.err_msg}")

    def restart_application(self):
        print("🔄 正在重启应用 ...")
        stop_result = self.app_interface.stop_workload()
        if stop_result.status_code != 0:
            raise RuntimeError(
                f"failed to stop application because {stop_result.err_msg}"
            )
        start_result = self.app_interface.start_workload()
        if start_result.status_code != 0:
            raise RuntimeError(
                f"failed to start application because {start_result.err_msg}"
            )

    def recover_cluster(self):
        print("🔄 正在恢复集群 ...")
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
            print(f"第 {batch_id} 轮无需要重启生效的参数，跳过写入脚本。")
            return

        # 构建要追加的内容
        batch_header = f"\n# 批次 {batch_id} - 重启后生效参数\n"
        content = batch_header + '\n'.join(commands)

        if self.first_restart_save:
            init_cmd = f"echo '#!/bin/bash' > {script_path}"
            self.ssh_client.run_cmd(init_cmd)
            self.first_restart_save = False
            print(f"首次创建重启参数脚本: {script_path}")

        append_cmd = f"cat << 'EOF' >> {script_path}\n{content}\nEOF"
        self.ssh_client.run_cmd(append_cmd)
        
        print(f"已将 {len(commands)} 个参数写入重启脚本: {script_path}")


    def run(self):
        # 运行benchmark，摸底参数性能指标
        if self.pressure_test_mode:
            logging.info(f"[ParamOptimizer] waiting for pressure test finished ...")
            pressure_test_result = wait_for_pressure_test()

            if pressure_test_result.status_code != 0:
                raise RuntimeError(
                    f"[ParamOptimizer] failed to run pressure test, err msg is {pressure_test_result.err_msg}"
                )

            baseline = float(pressure_test_result.output.output)
            logging.info(
                f"[ParamOptimizer] pressure test finished, baseline is {baseline}"
            )
        else:
            baseline = self.benchmark()
            if self.need_recover_cluster:
                self.recover_cluster()

        # 保存每轮调优的结果，反思调优目标是否达到
        history = []
        last_result = baseline
        best_result = baseline
        compare_func, symbol = self.app_interface.get_calculate_type()
        ratio = self.calc_improve_rate(baseline, last_result, symbol)
        print(
            f"[{0}/{self.max_iterations}] 性能基线是：{baseline}, 最佳结果：{best_result}, 上一轮结果:{last_result if last_result is not None else '-'}, 性能提升：{ratio:.2%}"
        )

        for i in range(self.max_iterations):
            # 未达成目标的情况下，根据调优结果与历史最优的参数，执行参数调优推荐，给出参数名和参数值
            recommend_params = self.param_recommender.run(history_result=history)

            # 设置参数生效
            self.apply_params(recommend_params)
            if self.need_restart_application:
                self.restart_application()

            # 执行benchmark，反馈调优结果
            performance_result = self.benchmark()
            if self.need_recover_cluster:
                # 保存在一个/tmp目录下的脚本中
                script_path = '/tmp/euler-copilot-params.sh'
                self.save_restart_params_to_script(recommend_params, script_path, i + 1)
                self.recover_cluster()

            last_result = performance_result

            history.append(
                (
                    "提升{:.2%}".format(
                        self.calc_improve_rate(baseline, performance_result, symbol)
                    ),
                    recommend_params,
                )
            )
            if best_result is None:
                best_result = compare_func(baseline, performance_result)
            else:
                best_result = compare_func(best_result, performance_result)

            ratio = self.calc_improve_rate(baseline, last_result, symbol)

            # 达到预期效果，则退出循环
            if self.reached_goal(baseline, performance_result, symbol):
                print(
                    f"[{i+1}/{self.max_iterations}] 性能基线是：{baseline}, 最佳结果：{best_result}, 上一轮结果:{last_result if last_result is not None else '-'}, 性能提升：{ratio:.2%}"
                )
                break

            print(
                f"[{i+1}/{self.max_iterations}] 性能基线是：{baseline}, 最佳结果：{best_result}, 上一轮结果:{last_result if last_result is not None else '-'}, 性能提升：{ratio:.2%}"
            )

        print(
            f"调优完毕，{'达到' if self.reached_goal(baseline, best_result, symbol) else '未达到'} 预期目标"
        )
