import subprocess
import os
import re
import sys

"""
The tool is used for bisection analysising the commits.
"""

# Function to extract execution time from a text
def extract_execution_time(text):
    match = re.search(r"Compile script executed in (\d+) milliseconds\.", text)
    if match:
        execution_time = float(match.group(1))
        return execution_time
    else:
        return -1


# Function to fetch commits within a range
def get_commits(start_commit, stop_commit, project_path):
    print("Fetching commits...")
    commits_file_name = "commits.txt"
    commits_file_path = f"{project_path}/{commits_file_name}"

    # Check if commits file exits
    if os.path.exists(commits_file_path):
        with open(commits_file_path, 'r') as file:
            all_commits = file.read().split('\n')
        print("Commits loaded from file.")
    else:
        # If commits file doesn't exist, fetch commits from the repository
        os.chdir("{project_path}")
        all_commits = subprocess.getoutput("git rev-list --reverse HEAD")
        all_commits = all_commits.split('\n')
        with open(commits_file_name, 'w') as file:
            file.write('\n'.join(all_commits))
        os.chdir("../../src")
        print("Commits fetched from repository and saved to file.")

    # Find the indices of start_commit and stop_commit to get the commits within the range
    start_index = all_commits.index(start_commit)
    stop_index = all_commits.index(stop_commit)
    commits = all_commits[start_index:stop_index+1]
    print(f"Filtered commits from {start_commit} to {stop_commit}.")

    return commits


# Function to compile the project at a specific commit
def compile_project(commit, compile_script_path, log_path):
    print(f"Compiling FFmpeg at commit {commit}...")
    # Re-compile the project and redirect the comilation information to log_path
    with open(log_path, 'a') as file:
        subprocess.run([compile_script_path, commit], stdout=file, stderr=file)


# Function to run a benchmark script and extract execution time
def benchmark(benchmark_script_path):
    print("Running benchmark...")

    result = -1
    try:
        result = subprocess.getoutput("bash " + benchmark_script_path)
        result = extract_execution_time(result)
        print(f"Benchmark script executed in {result} milliseconds.")
    except Exception as e:
        print(f"Error while running benchmark script: {e}")
    return float(result)


# Main function
def main(start_commit, stop_commit, compile_script_path, project_path, benchmark_script_path, log_path):
    print("Starting search for commit with highest benchmark improvement...")

    commits = get_commits(start_commit, stop_commit, project_path)
    left = 0
    right = len(commits) - 1
    best_commit = None
    best_improvement = -1

    # Calculate the execution time at the start and end commits
    compile_project(commits[left], compile_script_path, log_path)
    start_benchmark = benchmark(benchmark_script_path)
    print(
        f"Start commit {commits[left]} executed in {start_benchmark} milliseconds.")

    compile_project(commits[right], compile_script_path, log_path)
    end_benchmark = benchmark(benchmark_script_path)
    print(
        f"End commit {commits[right]} executed in {end_benchmark} milliseconds.")

    best_benchmark = min(start_benchmark, end_benchmark)

    while left < right:
        mid = (left + right) // 2

        # Handle corner cases where the commit is not suitable for benchmarking
        mid_benchmark = -1
        while mid < right and mid_benchmark == -1:
            compile_project(commits[mid], compile_script_path, log_path)
            mid_benchmark = benchmark(benchmark_script_path)
            if mid_benchmark == -1:
                mid = mid + 1

        print(
            f"Mid commit {commits[mid]} executed in {mid_benchmark} milliseconds.")
        print(f"{commits[mid]}# {mid_benchmark}")

        start_improvement = start_benchmark - mid_benchmark
        end_improvement = mid_benchmark - end_benchmark

        # Determine which side (start or end) has the greatest improvement and update accordingly
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

        best_benchmark = min(best_benchmark, mid_benchmark)

    print(
        f"The commit with the highest benchmark improvement is {best_commit}")
    print(f"The benchmark of the best commit is {best_benchmark}")


# Entry point of the script
if __name__ == "__main__":
    start_hash = sys.argv[1]
    end_hash = sys.argv[2]
    compile_script_path = sys.argv[3]
    project_path = sys.argv[4]
    benchmark_script_path = sys.argv[5]
    log_path = sys.argv[6] if len(sys.argv) > 6 else "../logs/compile.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    main(start_hash, end_hash, compile_script_path,
         project_path, benchmark_script_path, log_path)