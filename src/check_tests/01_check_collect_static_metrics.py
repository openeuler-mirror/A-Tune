import json
from src.check_tests.check_tests_utils import check_collect_static_metrics

def main():
    result = check_collect_static_metrics()
    
    print(f"{json.dumps(result, indent=4, ensure_ascii=False)}")

if __name__ == "__main__":
    main()