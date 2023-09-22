import os


# clan_data: 用于清理 /data 目录下的文件：交叉对比参数的临时文件、统计结果
def clean_files_with_prefix(directory, prefix):
    for filename in os.listdir(directory):
        if filename.startswith(prefix) and filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                print(f"文件 {filename} 已成功删除")
            except OSError as e:
                print(f"删除文件 {filename} 时出现错误：{e}")


# 使用示例
data_directory = "./data/"
prefix_to_clean = ["differ-2023", "statistical-2023"]

for prefix in prefix_to_clean:
    clean_files_with_prefix(data_directory, prefix)
