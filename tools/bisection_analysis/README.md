# 二分法性能分析工具

这个工具旨在帮助用户自动化地分析两个软件版本之间的性能差异，并找出导致性能改进或降低的关键代码提交。通过采用二分法策略，该工具能够快速缩小搜索范围，从而大大减少了人工工作的工作量。

## 使用方法

### 安装依赖

在运行工具之前，请确保你的系统上安装了以下依赖项：

- Python 3.x
- Git
- Bash

### 获取代码

首先，从 GitHub 上获取此工具的代码。你可以使用以下命令来克隆存储库：

```bash
git clone https://gitee.com/openeuler/A-Tune.git
cd A-Tune/tools/bisection_analysis
```

### 运行二分法性能分析工具

运行二分法性能分析工具的命令如下：

```bash
python src/main.py [选项] 开始提交 停止提交 编译脚本路径 项目路径 基准测试脚本路径 日志路径
```

- `[选项]`：你可以使用 `--demo` 选项来运行演示模式（详见下文）。如果不使用 `--demo` 选项，则需要提供所有后面列出的参数。
- `开始提交` 和 `停止提交`：这两个参数指定了要分析的提交范围的起始和结束点。你需要提供这两个提交的哈希值。
- `编译脚本路径`：这是一个用于编译项目的 Bash 脚本的路径。该脚本将在每个提交上运行，以准备项目进行性能测试。
- `项目路径`：这是你的项目的根目录路径，包含了 Git 存储库。
- `基准测试脚本路径`：这是一个用于执行性能基准测试的 Bash 脚本的路径。该脚本将在每个提交上运行以测量性能。
- `日志路径`：这是保存工具输出和日志文件的目录路径。如果该目录不存在，工具将尝试创建它。

### 演示模式

你可以使用 `--demo` 选项来运行工具的演示模式。演示模式会自动设置工具的参数，并使用预定义的示例项目和基准测试脚本来演示工具的功能。在演示模式下，你不需要手动提供参数，工具将自动运行并输出结果。

```bash
python src/main.py --demo
```

## 演示模式

演示模式旨在向用户展示工具的功能，以便快速了解如何使用它。在演示模式下，工具会使用以下示例参数运行：

- 开始提交：a1928dff2c498ab9439d997bdc93fc98d2862cb0
- 停止提交：c7049013247ac6c4851cf1b4ad6e22f0461a775a
- 编译脚本路径：scripts/demo_compile.sh
- 项目路径：../..
- 基准测试脚本路径：scripts/demo_benchmark.sh
- 日志路径：logs

工具将自动下载示例项目（FFmpeg）并设置所需的目录结构。然后，它将执行二分法性能分析，找到导致性能改进的提交，并输出结果。

## 输出格式

工具的输出将包括以下信息：

- 执行过程中的日志信息，包括编译和基准测试的详细输出。
- 最终结果，包括找到的具有最大性能改进的提交的哈希值和相应的性能改进（以毫秒为单位）。

以下是一个示例输出：

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

工具将输出找到的具有最大性能改进的提交的哈希值，并显示相应的性能改进。请注意，性能改进的单位为毫秒。

## 注意事项

- 请确保提供正确的提交哈希值、脚本路径和目录路径。不正确的参数可能会导致工具无法正常工作。
- 如果在运行工具时遇到任何问题，请查看日志以获取详细信息，以便诊断和解决问题。
- 工具的性能分析结果仅供参考，应与实际应用场景进行比较和验证。

## 示例脚本

在本工具的示例中，我们提供了两个示例脚本，用于演示编译和基准测试：

- `demo_compile.sh`：用于编译项目的示例脚本。
- `demo_benchmark.sh`：用于执行基准测试的示例脚本。

你可以根据自己的项目和需求来编写自定义的编译和基准测试脚本，并在运行工具时提供正确的路径。