from src.utils.prompt_instance import prompt_manager

common_allowed_set = {
    "service_name": "TESTTEST-service_name-TESTTEST",
    "performance_metric.name": "TESTTEST-performance_metric.name-TESTTEST",
    "performance_metric.value": "TESTTEST-performance_metric.value-TESTTEST",
    "slo_goal": "TESTTEST-slo_goal-TESTTEST",
    "static_profile": "TESTTEST-static_profile-TESTTEST",
    "performance_analysis_report": "TESTTEST-performance_analysis_report-TESTTEST",
    "params_set_str": "TESTTEST-params_set_str-TESTTEST"
}

def test_get_fast_prompt(service_name):
    allowed_set = common_allowed_set
    allowed_set["history_result"] = "TESTTEST-history_result-TESTTEST"

    prompt_manager.format_prompt(service_name, "fast", "recommender", allowed_set)

def test_get_idea_prompt(service_name):
    allowed_set = common_allowed_set

    prompt_manager.format_prompt(service_name, "normal", "idea", allowed_set)
    
def test_get_normal_prompt(service_name):
    allowed_set = common_allowed_set
    allowed_set["optimization_idea"] = "TESTTEST-optimization_idea-TESTTEST"
    allowed_set["history_result"] = "TESTTEST-history_result-TESTTEST"
    
    prompt_manager.format_prompt(service_name, "normal", "recommender_positive", allowed_set)
    prompt_manager.format_prompt(service_name, "normal", "recommender_negative", allowed_set)

def test_test_mem_mode(service_name):
    allowed_set = common_allowed_set
    allowed_set["application"] = "TESTTEST-application-TESTTEST"
    
    mem0_prompt = prompt_manager.format_prompt(service_name, "slow", "mem", allowed_set)
    
def test_slow_prompt_mode(service_name):
    allowed_set = common_allowed_set
    allowed_set["long_mem"] = "TESTTEST-long_mem-TESTTEST"
    allowed_set["short_mem"] = "TESTTEST-short_mem-TESTTEST"
    
    prompt_manager.format_prompt(service_name, "slow", "recommender", allowed_set)

def main():
    for server_name in ["mysql", "nginx"]:
        test_get_fast_prompt(server_name)
        test_get_idea_prompt(server_name)
        test_get_normal_prompt(server_name)
        test_test_mem_mode(server_name)
        test_slow_prompt_mode(server_name)

if __name__ == "__main__":
    main()