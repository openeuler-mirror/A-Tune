from src.check_tests.check_tests_utils import check_analyze_performance

def main():
    report, bottlenecksult = check_analyze_performance()
    
    print(f">>> PerformanceAnalyzer运行结果：\n{report}\n分析结论：\n{bottlenecksult}")

if __name__ == "__main__":
    main()