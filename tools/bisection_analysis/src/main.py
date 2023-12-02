"""
The tool is used for bisection analysising the commits.
"""

import subprocess
import os
import re
import logging
import argparse
import shutil
import urllib.request
from collections import namedtuple


def extract_execution_time(text):
    """Extract the execution time from a given text."""
    match = re.search(r"Script executed in (\d+) milliseconds.", text)
    return float(match.group(1)) if match else -1


# Configure the logging module
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_commits(commit_start, commit_stop, path_project, log_path):
    """Fetches commits within a given range."""
    logging.info("Fetching commits...")
    commits_file_name = "commits.txt"
    commits_file_path = f"{log_path}/{commits_file_name}"

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
            fd = os.open(f"../../logs/commits.txt",
                         os.O_WRONLY | os.O_CREAT, 0o644)
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
    log_file_name = "/compile.log"
    log_file_path = f"{output_log_path}/{log_file_name}"

    # Create a file with rw-r--r-- permission
    fd = os.open(log_file_path, os.O_WRONLY |
                 os.O_CREAT | os.O_APPEND, 0o644)
    try:
        # Re-compile the project and redirect the compilation information to log_file_path
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


def download_and_setup_demo_mode():
    """Download and set up the requirements of demo mode."""
    ffmpeg_url = "https://github.com/FFmpeg/FFmpeg.git"
    project_path = "../projects/FFmpeg"

    # Check and create the project directory
    os.makedirs(os.path.dirname(project_path), exist_ok=True)

    # Find the git executable dynamiclly
    git_executable = shutil.which("git")
    if git_executable is None:
        raise Exception(
            "Git executable not found. Please make sure git is intalled and in your system's PATH.")

    if os.path.exists(project_path):
        # FFmpeg directory exists, checkout master branch and pull the latest changes
        logging.info("Updating FFmpeg...")
        subprocess.run(
            [git_executable, "-C", project_path, "checkout", "master"])
        subprocess.run([git_executable, "-C", project_path, "pull"])
    else:
        # FFmpeg directory does not exits, clone the repository
        logging.info("Download FFmpeg...")

        subprocess.run([git_executable, "clone", ffmpeg_url, project_path])

    logging.info("FFmpeg downloaded and set up successfully.")

    # Set up the demo video directory and download the demo video
    video_url = "https://github.com/anjieyang/Demo-Video-A-Tune/blob/main/akiyo_cif.y4m"
    video_dir = "../data/"
    video_path = os.path.join(video_dir, "akiyo_cif.y4m")

    # Ensure the video directory exists
    os.makedirs(video_dir, exist_ok=True)
    
    if not os.path.exists(video_path):
        logging.info("Downloading demo videos...")
        urllib.request.urlretrieve(video_url, video_path)
        logging.info("Demo video downloaded and set up successfully.")
    else:
        logging.info("Demo video already exists, no need to re-download.")

    return project_path


# Define a named tuple to hold the function parameters
MainArguments = namedtuple('MainArguments', ['start_commit', 'stop_commit', 'compile_script_path',
                                             'project_path', 'benchmark_script_path', 'log_path'])


def main(args):
    """Main function to search for the commit with the highest benchmark improvement."""
    logging.info(
        "Starting search for commit with highest benchmark improvement...")

    # Get the list of commits within the specified range
    commits = get_commits(
        args.start_commit, args.stop_commit, args.project_path, args.log_path)

    left = 0
    right = len(commits) - 1
    best_commit = None
    best_improvement = -1

    # Calculate the execution time at the start commit
    compile_project(commits[left], args.compile_script_path, args.log_path)
    start_benchmark = benchmark(args.benchmark_script_path)
    logging.info(
        f"Start commit {commits[left]} executed in {start_benchmark} milliseconds.")

    # Calculate the execution time at the end commit
    compile_project(commits[right], args.compile_script_path, args.log_path)
    end_benchmark = benchmark(args.benchmark_script_path)
    logging.info(
        f"End commit {commits[right]} executed in {end_benchmark} milliseconds.")

    best_benchmark = min(start_benchmark, end_benchmark)

    while left < right:
        mid = (left + right) // 2

        # Handle cases where the commit may not be suitable for benchmarking
        mid_benchmark = -1
        while mid < right and mid_benchmark == -1:
            compile_project(
                commits[mid], args.compile_script_path, args.log_path)
            mid_benchmark = benchmark(args.benchmark_script_path)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bisection analysis tool.')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode')
    parser.add_argument('start_commit', nargs='?', help='Start commit hash')
    parser.add_argument('stop_commit', nargs='?', help='Stop commit hash')
    parser.add_argument('compile_script_path', nargs='?',
                        help='Path to the compilation script')
    parser.add_argument('project_path', nargs='?',
                        help='Path to the project directory')
    parser.add_argument('benchmark_script_path', nargs='?',
                        help='Path to the benchmarking script')
    parser.add_argument('log_path', nargs='?',
                        default="../logs", help='Path to the log file')

    args = parser.parse_args()

    if args.demo:
        logging.info("Running in demo mode...")

        # Download and set up FFmpeg, and get the project path
        args.project_path = download_and_setup_demo_mode()

        # Set other parameters for the demo mode
        args.start_commit = "a1928dff2c498ab9439d997bdc93fc98d2862cb0"
        args.stop_commit = "c7049013247ac6c4851cf1b4ad6e22f0461a775a"
        args.compile_script_path = "../scripts/demo_compile.sh"
        args.benchmark_script_path = "../scripts/demo_benchmark.sh"

        # Create the directory for the log file if it doesn't exist
        if not os.path.exists(args.log_path):
            os.mkdir(args.log_path)
    else:
        # Ensure all necessary arguments are provided
        if not all([
            args.start_commit,
            args.stop_commit,
            args.compile_script_path,
            args.project_path,
            args.benchmark_script_path
        ]):
            parser.error(
                "All positional arguments are required if not running in demo mode.")

        # Create the directory for the log file if it doesn't exist
        if not os.path.exists(args.log_path):
            os.mkdir(args.log_path)

    # Call the main function with the parsed argument
    main(args)
