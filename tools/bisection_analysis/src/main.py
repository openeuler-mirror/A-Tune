import subprocess
import os
import re
import sys


def extract_execution_time(text):
    match = re.search(r"Compile script executed in (\d+) milliseconds\.", text)
    if match:
        execution_time = float(match.group(1))
        return execution_time
    else:
        return None


def get_commits(start_commit, stop_commit):
    print("Fetching commits...")
    commits_file_name = "commits.txt"
    commits_file_path = f"../projects/FFmpeg/{commits_file_name}"
    if os.path.exists(commits_file_path):
        with open(commits_file_path, 'r') as file:
            all_commits = file.read().split('\n')
        print("Commits loaded from file.")
    else:
        os.chdir("../projects/FFmpeg")
        all_commits = subprocess.getoutput("git rev-list --reverse HEAD")
        all_commits = all_commits.split('\n')
        with open(commits_file_name, 'w') as file:
            file.write('\n'.join(all_commits))
        os.chdir("../../src")
        print("Commits fetched from repository and saved to file.")

    # 找到 start_commit 和 stop_commit 的索引，获取相应范围的提交
    start_index = all_commits.index(start_commit)
    stop_index = all_commits.index(stop_commit)
    commits = all_commits[start_index:stop_index+1]
    print(f"Filtered commits from {start_commit} to {stop_commit}.")

    return commits


def compile_project(commit):
    print(f"Compiling FFmpeg at commit {commit}...")
    # 重新编译项目
    subprocess.run(["../scripts/compile-ffmpeg.sh", commit])


def benchmark():
    print("Running benchmark...")
    result = subprocess.getoutput("../scripts/benchmark.sh")
    result = extract_execution_time(result)
    print(f"Benchmark script executed in {result} milliseconds.")
    return float(result)  # 假设基准测试脚本返回浮点数


def main(start_commit, stop_commit):
    print("Starting search for commit with highest benchmark improvement...")

    commits = get_commits(start_commit, stop_commit)
    left = 0
    right = len(commits) - 1
    best_commit = None
    best_improvement = -1

    # 计算 start 和 end 的运行时间
    compile_project(commits[left])
    start_benchmark = benchmark()
    print(f"Start commit {commits[left]} executed in {start_benchmark} milliseconds.")

    compile_project(commits[right])
    end_benchmark = benchmark()
    print(f"End commit {commits[right]} executed in {end_benchmark} milliseconds.")

    while left < right:
        mid = (left + right) // 2

        compile_project(commits[mid])
        mid_benchmark = benchmark()
        print(f"Mid commit {commits[mid]} executed in {mid_benchmark} milliseconds.")

        start_improvement = start_benchmark - mid_benchmark
        end_improvement = mid_benchmark - end_benchmark

        # 看哪个提升大，就跳到哪个里面
        if start_improvement > end_improvement:
            if start_improvement > best_improvement:
                best_commit = commits[mid]
                best_improvement = start_improvement
            right = mid
        else:
            if end_improvement > best_improvement:
                best_commit = commits[mid]
                best_improvement = end_improvement
            left = mid + 1

    print(f"The commit with the highest benchmark improvement is {best_commit}")


if __name__ == "__main__":
    start_hash = sys.argv[1]
    end_hash = sys.argv[2]
    main(start_hash, end_hash)