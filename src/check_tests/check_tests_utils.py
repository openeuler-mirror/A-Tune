from src.config import config
from src.start_tune import (
    create_ssh_client,
    collect_static_metrics,
    collect_runtime_metrics,
    analyze_performance
)
from src.performance_optimizer.param_knowledge import ParamKnowledge
from src.utils.config.app_config import AppInterface
from src.performance_optimizer.param_recommender import ParamRecommender
from src.performance_optimizer.param_optimizer import ParamOptimizer

def get_feature_cfg():
    return config["feature"][0]

def get_server_cfg():
    return config["servers"][0]

def check_collect_static_metrics():
    ssh_client = create_ssh_client(get_server_cfg())
    return collect_static_metrics(ssh_client)

def check_collect_runtime_metrics():
    server_cfg = get_server_cfg()
    feature_cfg = get_feature_cfg()
    ssh_client = create_ssh_client(server_cfg)
    return collect_runtime_metrics(ssh_client, server_cfg, feature_cfg["pressure_test_mode"])

def check_analyze_performance():
    metrics_data = check_collect_runtime_metrics()
    server_cfg = get_server_cfg()
    report, bottleneck = analyze_performance(metrics_data, server_cfg["app"])
    return report, bottleneck

def check_describe_param_background_knob():
    service_name = get_server_cfg()["app"]
    feature_cfg = get_feature_cfg()
    param_knowledge = ParamKnowledge(
        ssh_client=create_ssh_client(get_server_cfg()),
        tune_system_param=feature_cfg["tune_system_param"],
        tune_app_param=feature_cfg["tune_app_param"]
    )
    
    all_params = param_knowledge.get_params(service_name)
    params_describe_list = param_knowledge.describe_param_background_knob(
        service_name, all_params
    )[0]
    
    return params_describe_list

def check_param_recommender():
    server_cfg = get_server_cfg()
    feature_cfg = get_feature_cfg()
    service_name = server_cfg["app"]
    ssh_client = create_ssh_client(server_cfg)
    app_interface = AppInterface(ssh_client).get(service_name)
    static_profile = check_collect_static_metrics()
    analysis_report = check_analyze_performance()[0]
    param_knowledge = ParamKnowledge(
        ssh_client=create_ssh_client(get_server_cfg()),
        tune_system_param=feature_cfg["tune_system_param"],
        tune_app_param=feature_cfg["tune_app_param"]
    )
    all_params = param_knowledge.get_params(service_name)
    params_set = param_knowledge.describe_param_background_knob(
        service_name, all_params
    )[0]
    
    param_recommender = ParamRecommender(
        service_name=service_name,
        slo_goal=0.1,
        performance_metric=app_interface.performance_metric,
        static_profile=static_profile,
        performance_analysis_report=analysis_report,
        ssh_client=ssh_client,
        all_params=all_params,
        params_set=params_set
    )
    
    recommend_params = param_recommender.run(history_result={}, is_positive=True)
    
    return recommend_params

def check_apply_params():
    server_cfg = get_server_cfg()
    feature_cfg = get_feature_cfg()
    service_name = server_cfg["app"]
    ssh_client = create_ssh_client(server_cfg)
    analysis_report = check_analyze_performance()[0]
    static_profile = check_collect_static_metrics()

    def slo_calc_callback(baseline, benchmark_result, symbol):
        if baseline is None or abs(baseline) < 1e-9:
            return 0.0
        return symbol * (benchmark_result - baseline) / baseline

    optimizer = ParamOptimizer(
        service_name=service_name,
        slo_goal=0.1,
        analysis_report=analysis_report,
        static_profile=static_profile,
        ssh_client=ssh_client,
        slo_calc_callback=slo_calc_callback,
        need_restart_application=feature_cfg["need_restart_application"],
        pressure_test_mode=feature_cfg["pressure_test_mode"],
        tune_system_param= feature_cfg["tune_system_param"],
        tune_app_param= feature_cfg["tune_app_param"],
        need_recover_cluster=feature_cfg["need_recover_cluster"],
        benchmark_timeout=feature_cfg["benchmark_timeout"]
    )

    recommend_params = optimizer.param_recommender.run(history_result={}, is_positive=True)
    print(f"推荐设置的参数为：{recommend_params}")
    optimizer.apply_params(recommend_params)
    if optimizer.need_restart_application:
        optimizer.restart_application()
