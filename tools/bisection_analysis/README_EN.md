# Bisect-based Performance Analysis Tool

This tool automatically analyzes performance differences between two software versions and identifies the key code commits responsible for improvements or regressions. By leveraging a bisection strategy, it efficiently narrows the search space, significantly reducing manual effort.

## How to Use

### Installing Dependencies

Before running the tool, ensure that the following dependencies are installed on your system:

- Python 3.x
- Git
- Bash

### Obtaining Code

First, obtain the tool code from GitHub. You can run the following command to clone the repository:

```bash
git clone https://gitcode.com/openeuler/A-Tune.git
cd A-Tune/tools/bisection_analysis
```

### Running the Tool

Run the following command to start the bisect-based performance analysis tool:

```bash
python src/main.py [Option] Start_committing Stop_committing Compilation_script_path Project_path Benchmark_test_script_path Log_path
```

- `[Option]`: You can use the `--demo` option to run the demo (see the following description for details). If you do not use the `--demo` option, provide all the parameters listed below.
- `Start_committing` and `Stop_committing`: The two parameters specify the start and end commits of the range to be analyzed. You need to provide the hashes of the two commits.
- `Compilation_script_path`: It is the path to the Bash script used to compile the project. The script is executed on each commit to prepare the project for performance testing.
- `Project_path`: It is the root directory of the project, which contains the Git repository.
- `Benchmark_test_script_path`: It is the path to the Bash script used to execute the performance benchmark test. The script is executed on each commit to measure performance.
- `Log_path`: It is the directory for storing tool outputs and log files. If the directory does not exist, the tool attempts to create it.

### Demo

You can use the `--demo` option to run the tool in demo mode. The demo mode automatically configures the tool parameters and uses the predefined sample project and benchmark test script to demonstrate tool functions. In demo mode, you do not need to manually provide parameters; the tool runs automatically and outputs the results.

```bash
python src/main.py --demo
```

## Demo Mode

The demo mode is designed to help users quickly understand how to use the tool by showcasing its functionality. In this mode, the tool runs with the following example parameters:

- `Start_committing`: a1928dff2c498ab9439d997bdc93fc98d2862cb0
- `Stop_committing`: c7049013247ac6c4851cf1b4ad6e22f0461a775a
- `Compilation_script_path`: scripts/demo_compile.sh
- `Project_path`: ../..
- `Benchmark_test_script_path`: scripts/demo_benchmark.sh
- `Log_path`: logs

The tool automatically downloads a sample project (FFmpeg) and sets up the required directory structure. It then performs a bisection-based performance analysis, identifies the commits responsible for performance improvements, and outputs the results.

## Output Format

The output produced by the tool includes the following information:

- Log information during execution, including detailed outputs from compilation and benchmarking.
- Final result, including the hash of the commit with the greatest performance improvement and the corresponding improvement in milliseconds.

The following is an example:

```bash
Starting search for commit with highest benchmark improvement...
Fetching commits...
Commits loaded from file.
Compiling FFmpeg at commit a1928dff2c498ab9439d997bdc93fc98d2862cb0...
Start commit a1928dff2c498ab9439d997bdc93fc98d2862cb0 executed in 500.0 milliseconds.
Compiling FFmpeg at commit c7049013247ac6c4851cf1b4ad6e22f0461a775a...
End commit c7049013247ac6c4851cf1b4ad6e22f0461a775a executed in 550.0 milliseconds.
Mid commit <commit_hash> executed in 525.0 milliseconds.
<commit_hash># 525.0
Mid commit <commit_hash> executed in 530.0 milliseconds.
<commit_hash># 530.0
...
The commit with the highest benchmark improvement is <best_commit>
The benchmark of the best commit is <best_benchmark> milliseconds.
```

The tool outputs the hash of the commit with the greatest performance improvement and displays the corresponding performance improvement in milliseconds.

## Precautions

- Ensure that the correct hashes, script path, and directory path are provided. Incorrect parameters may cause the tool to fail.
- If you encounter any issues while running the tool, check the logs for detailed diagnostic and troubleshooting information.
- The performance analysis results outputted by the tool are for reference only. You should compare and verify them against real-world application scenarios.

## Sample Scripts

In this demo, two sample scripts are provided to demonstrate compilation and benchmarking:

- `demo_compile.sh`: Sample script used to compile the project.
- `demo_benchmark.sh`: Sample script for running benchmarking.

You can write custom compilation and benchmarking scripts based on your project and requirements, and provide the correct paths when running the tool.
