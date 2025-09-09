import json

def process_data(data):
    processed_data = {}
    for item in data:
        param_name = item["name"]
        param_info = item["info"]

        processed_data[param_name] = {}
        processed_data[param_name]["desc"] = param_info["desc"]
        processed_data[param_name]["type"] = param_info["type"]
        processed_data[param_name]["dtype"] = param_info["dtype"]
        processed_data[param_name]["range"] = param_info["min_value"] if isinstance(param_info["min_value"], list) else [param_info["min_value"], param_info["max_value"]]
    return processed_data

def process_data1(data):
    processed_data = {}
    for item in data:
        param_name = item["name"]
        param_info = item["info"]

        processed_data[param_name] = {}
        processed_data[param_name]["desc"] = param_info["desc"]
        processed_data[param_name]["type"] = param_info["type"]
        processed_data[param_name]["dtype"] = param_info["dtype"]
        processed_data[param_name]["range"] = param_info["options"] if param_info["type"] == "discrete" else [param_info["min_value"], param_info["max_value"]]
    return processed_data

def process_json(input_path, output_path):
    """
    读取input_path指定的JSON文件，对数据进行处理，然后将处理后的数据保存到output_path指定的文件中。
    """
    try:
        # 读取JSON文件
        with open(input_path, 'r', encoding='utf-8') as infile:
            data = json.load(infile)

        processed_data = process_data1(data)

        # 将处理后的数据保存到output_path
        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(processed_data, outfile, ensure_ascii=False, indent=4)

        print(f"处理完成，结果已保存到 {output_path}")

    except FileNotFoundError:
        print(f"错误：文件 {input_path} 未找到。")
    except json.JSONDecodeError:
        print(f"错误：文件 {input_path} 不是有效的JSON格式。")
    except Exception as e:
        print(f"发生错误：{e}")


# 示例调用
if __name__ == "__main__":
    input_path = "../mysql_knowledge/spark_param.json"  # 输入文件路径
    output_path = "../mysql_knowledge/spark.json"  # 输出文件路径
    process_json(input_path, output_path)
