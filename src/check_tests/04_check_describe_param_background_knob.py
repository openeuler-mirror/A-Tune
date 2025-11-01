from src.check_tests.check_tests_utils import check_describe_param_background_knob

def main():
    params_describe_list = check_describe_param_background_knob()
    
    params_describe_list_res = ("\n\n").join(params_describe_list)
    
    print(f"{params_describe_list_res}")

if __name__ == "__main__":
    main()