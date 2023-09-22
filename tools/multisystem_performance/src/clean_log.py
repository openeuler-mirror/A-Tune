import os

def clean_files_with_prefix(directory, prefix):
    for filename in os.listdir(directory):
        if filename.startswith(prefix) and filename.endswith(".log"):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                print(f"文件 {filename} 已成功删除")
            except OSError as e:
                print(f"删除文件 {filename} 时出现错误：{e}")

# 使用示例
data_directory = "./log/"
prefix_to_clean = ["get_sysctl_ulimit","load_config"]

for prefix in prefix_to_clean:
    clean_files_with_prefix(data_directory, prefix)
