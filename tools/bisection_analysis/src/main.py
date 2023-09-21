"""
The tool is used for bisection analysising the commits.
"""

import subprocess
import os
import re
import sys
import logging
from collections import namedtuple


def extract_execution_time(text):
    """Extract the execution time from a given text."""
    match = re.search(r"Compile script executed in (\d+) milliseconds\.", text)
    return float(match.group(1)) if match else -1


# Configure the logging module
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_commits(commit_start, commit_stop, path_project):
    """Fetches commits within a given range."""
    logging.info("Fetching commits...")
    commits_file_name = "commits.txt"
    commits_file_path = f"{path_project}/{commits_file_name}"

    # Check if commits file exits
    if os.path.exists(commits_file_path):
        with open(commits_file_path, 'r') as file:
            all_commits = file.read().split('\n')
        logging.info("Commits loaded from file.")
    else:
        try:
            os.chdir(path_project)
            all_commits = subprocess.getoutput(
                "git rev-list --reverse HEAD").split('\n')
            # Create a file with rw-r--r-- permission
            fd = os.open(commits_file_path, os.O_WRONLY | os.O_CREAT, 0o644)
            try:
                with os.fdopen(fd, 'w') as file:
                    file.write('\n'.join(all_commits))
            except:
                # Close the file descriptor in case of an exception
                os.close(fd)
                raise   # Re-raise the exception to be caught by the outer try block
            os.chdir("../../src")
            logging.info(
                "Commits fetched from the repository and saved to file.")
        except Exception as e:
            logging.error(f"Error fetching commits: {e}")
            return []

    # Find the indices of commit_start and commit_stop to get the commits within the range
    try:
        start_index = all_commits.index(commit_start)
        stop_index = all_commits.index(commit_stop)
        commits = all_commits[start_index:stop_index + 1]
        logging.info(f"Filtered commits from {commit_start} to {commit_stop}.")
        return commits
    except ValueError:
        logging.error(
            "Start commit or stop commit not found in the list of commits.")
        return []


def compile_project(commit, script_path, output_log_path):
    """Compiles the project at a specific commit."""
    logging.info(f"Compiling FFmpeg at commit {commit}...")
    # Create a file with rw-r--r-- permission
    fd = os.open(output_log_path, os.O_WRONLY |
                 os.O_CREAT | os.O_APPEND, 0o644)
    try:
        # Re-compile the project and redirect the compilation information to output_log_path
        with os.fdopen(fd, 'a') as file:
            subprocess.run([script_path, commit], stdout=file, stderr=file)
    except:
        os.close(fd)
        raise


def benchmark(script_path):
    """Runs a benchmark script and extracts the execution time."""
    logging.info("Running benchmark...")
    try:
        result = subprocess.getoutput("bash " + script_path)
        result = extract_execution_time(result)
        logging.info(f"Benchmark script executed in {result} milliseconds.")
        return float(result)  # Assuming the benchmark script returns a float
    except Exception as e:
        logging.error(f"Error while running benchmark script: {e}")
        return -1


# Define a named tuple to hold the function parameters
MainArguments = namedtuple('MainArguments', ['start_commit', 'stop_commit', 'compile_script_path',
                                             'project_path', 'benchmark_script_path', 'log_path'])


def main(args):
    """Main function to search for the commit with the highest benchmark improvement."""
    logging.info(
        "Starting search for commit with highest benchmark improvement...")

    # Get the list of commits within the specified range
    commits = get_commits(
        args.start_commit, args.stop_commit, args.project_path)

    left = 0
    right = len(commits) - 1
    best_commit = None
    best_improvement = -1

    # Calculate the execution time at the start commit
    compile_project(commits[left], compile_script_path, log_path)
    start_benchmark = benchmark(benchmark_script_path)
    logging.info(
        f"Start commit {commits[left]} executed in {start_benchmark} milliseconds.")

    # Calculate the execution time at the end commit
    compile_project(commits[right], compile_script_path, log_path)
    end_benchmark = benchmark(benchmark_script_path)
    logging.info(
        f"End commit {commits[right]} executed in {end_benchmark} milliseconds.")

    best_benchmark = min(start_benchmark, end_benchmark)

    while left < right:
        mid = (left + right) // 2

        # Handle cases where the commit may not be suitable for benchmarking
        mid_benchmark = -1
        while mid < right and mid_benchmark == -1:
            compile_project(commits[mid], compile_script_path, log_path)
            mid_benchmark = benchmark(benchmark_script_path)
            if mid_benchmark == -1:
                mid = mid + 1

        logging.info(
            f"Mid commit {commits[mid]} executed in {mid_benchmark} milliseconds.")
        logging.info(f"{commits[mid]}# {mid_benchmark}")

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

    # Logging out the results
    logging.info(
        f"The commit with the highest benchmark improvement is {best_commit}")
    logging.info(f"The benchmark of the best commit is {best_benchmark}")


# Entry point of the script
if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) < 6:
        logging.error("Usage: python script.py <start_commit> <stop_commit> "
                      "<compile_script_path> <project_path> <benchmark_script_path> [log_path]")
        sys.exit(1)

    # Parse command-line arguments
    start_commit = sys.argv[1]
    stop_commit = sys.argv[2]
    compile_script_path = sys.argv[3]  # Path to the compilation script
    project_path = sys.argv[4]  # Path to the project directory
    benchmark_script_path = sys.argv[5]  # Path to the benchmarking script
    log_path = sys.argv[6] if len(sys.argv) > 6 else "../logs/compile.log"

    # Create the directory for the log file if it doesn't exist
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Call the main function with the parsed arguments
    args = MainArguments(start_commit, stop_commit, compile_script_path,
                         project_path, benchmark_script_path, log_path)

    main(args)
