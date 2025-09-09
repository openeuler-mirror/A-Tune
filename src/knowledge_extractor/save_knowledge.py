import json
import re
import os

def split_json_to_files(json_text: str, output_dir: str) -> None:
    """
    将包含多个参数的JSON文本分割并存储到不同的JSON文件中。
    如果文件已存在，比较新旧内容，选择内容较多的那个进行保存。

    Parameters:
        json_text (str): 包含多个参数的JSON文本。
        output_dir (str): 输出文件的目录。

    Returns:
        None
    """
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 解析JSON文本
    if json_text is None:
        return
    try:
        json_data = json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误：{e}")
        return

    # 遍历JSON对象并为每个参数创建或更新JSON文件
    for param in json_data:
        # 创建文件名
        if "/" in param['name'] or "\\" in param['name']:
            continue
        file_name = f"{param['name']}.json"
        file_path = os.path.join(output_dir, file_name)
        
        # 读取文件现有内容（如果存在）
        existing_content = ""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                existing_content = file.read()
        
        # 将参数转换为JSON字符串
        new_content = json.dumps(param, ensure_ascii=False, indent=4)
        
        # 比较新旧内容长度，选择较长的内容进行保存
        if len(new_content) > len(existing_content):
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
                print(f"已将参数 {param['name']} 更新到文件 {file_path}")
        else:
            print(f"文件 {file_path} 已存在且内容较多，未更新")