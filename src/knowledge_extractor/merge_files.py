import json
import os

def merge_json_files(input_directory, output_file):
    """
    Merge multiple JSON files into a single JSON file.

    :param input_directory: Directory containing JSON files to be merged.
    :param output_file: Path to the output JSON file.
    """
    merged_data = []

    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_directory):
        if filename.endswith(".json"):
            file_path = os.path.join(input_directory, filename)
            try:
                # 打开并读取JSON文件
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # 将内容添加到合并列表中
                    merged_data.append(data)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_path}: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

    # 将合并后的数据写入输出文件
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(merged_data, outfile, indent=4, ensure_ascii=False)

    print(f"Merged data has been written to {output_file}")

def json_to_jsonl(input_file, output_file):
    """
    将 JSON 文件转换为 JSON Lines 文件
    """
    # 读取 JSON 文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # 将列表中的每个对象写入 JSON Lines 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')  # 每个 JSON 对象占一行