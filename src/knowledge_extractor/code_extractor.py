import os

def extract_code_snippets(param_list: list, folder_path: str, output_file: str, context_lines: int = 20) -> None:
    """
    提取指定文件夹中与给定参数列表相关的代码片段，并将结果写入到指定的输出文件中。

    Parameters:
        param_list (list): 参数列表，例如 ["spark.driver.memoryOverheadFactor", "spark.executor.memory"]
        folder_path (str): 要查询的文件夹路径
        output_file (str): 输出文件路径
        context_lines (int, optional): 提取代码片段时包含的上下文行数。默认为20。

    Returns:
        None
    """
    results = {}

    # 遍历文件夹中的所有文件
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
            except Exception as e:
                print(f"无法读取文件 {file_path}: {e}")
                continue

            # 检查文件内容
            related_ranges = []
            for i, line in enumerate(lines):
                # 检查当前行是否包含参数
                for param in param_list:
                    if param in line:
                        # 计算上下文范围
                        start = max(0, i - context_lines)
                        end = min(len(lines), i + context_lines + 1)
                        related_ranges.append((start, end))
                        break


            # 合并重叠的范围
            if related_ranges:
                # 按起始行排序
                print(related_ranges)
                related_ranges.sort(key=lambda x: x[0])
                merged_ranges = []
                for current_start, current_end in related_ranges:
                    if not merged_ranges:
                        merged_ranges.append((current_start, current_end))
                    else:
                        last_start, last_end = merged_ranges[-1]
                        # 如果当前范围与最后一个合并范围有重叠或相邻，则合并
                        if current_start <= last_end:
                            merged_ranges[-1] = (last_start, max(last_end, current_end))
                        else:
                            merged_ranges.append((current_start, current_end))

                #print(merged_ranges)
                # 提取合并后的代码片段
                related_lines = []
                for start, end in merged_ranges:
                    related_lines.extend(lines[start:end])
                    related_lines.extend("-" * 50+ "\n" )

                unique_lines = []
                for line in related_lines:
                    unique_lines.append(line)
                results[file_path] = unique_lines

    # 将结果写入到输出文件中
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file_path, lines in results.items():
            for line in lines:
                outfile.write(line)


# 示例用法
if __name__ == "__main__":
    # 示例参数列表
    params = ["spark.dynamicAllocation.minExecutors","spark.dynamicAllocation.maxExecutors","spark.dynamicAllocation.initialExecutors","spark.shuffle.service.db.enabled"]

    # 示例文件夹路径
    folder = "../code"

    # 输出文件路径
    output = "./output.txt"

    # 提取代码片段并写入到文件
    extract_code_snippets(params, folder, output)