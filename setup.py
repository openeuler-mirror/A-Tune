import os

from setuptools import setup, find_packages
from glob import glob

cfg_path = "/etc/euler-copilot-tune"
for root, dirs, files in os.walk(cfg_path):
    for file in files:
        os.remove(os.path.join(root, file))
ser = "/usr/lib/systemd/system/tune-mcpserver.service"
if os.path.isfile(ser):
    os.remove(ser)
ser = "/usr/lib/systemd/system/tune-openapi.service"
if os.path.isfile(ser):
    os.remove(ser)


def get_recursive_files_with_relpath(src_root_dir):
    file_mapping = []
    for file_path in glob(f'{src_root_dir}/**/*', recursive=True):
        if os.path.isfile(file_path):  # 只处理文件（目录会自动创建）
            relative_path = os.path.relpath(file_path, src_root_dir)
            file_mapping.append((file_path, relative_path))
    return file_mapping


# -------------------------- 配置 data_files --------------------------
knowledge_src_root = 'src/knowledge_base'
knowledge_files = get_recursive_files_with_relpath(knowledge_src_root)
knowledge_data = []
for src_file, rel_path in knowledge_files:
    target_dir = os.path.join('/etc/euler-copilot-tune/knowledge_base/', os.path.dirname(rel_path))
    knowledge_data.append((target_dir, [src_file]))
config_src_root = 'config'
config_files = get_recursive_files_with_relpath(config_src_root)
config_data = []
for src_file, rel_path in config_files:
    target_dir = os.path.join('/etc/euler-copilot-tune/config/', os.path.dirname(rel_path))
    config_data.append((target_dir, [src_file]))

scripts_src_root = 'scripts'
scripts_files = get_recursive_files_with_relpath(scripts_src_root)
scripts_data = []
for src_file, rel_path in scripts_files:
    target_dir = os.path.join('/etc/euler-copilot-tune/scripts/', os.path.dirname(rel_path))
    scripts_data.append((target_dir, [src_file]))
data_files = [('/etc/euler-copilot-tune/config/', glob('config/*')),
              ('/etc/euler-copilot-tune/config/', glob('config/.env.yaml')),
              ('/etc/euler-copilot-tune/scripts/', glob('scripts/*/*')),
              ('/usr/lib/systemd/system/', glob('service/*'))] + knowledge_data + config_data + scripts_data
setup(
    name="euler-copilot-tune",
    version="1.0",
    author="xu hou",
    author_email="houxu5@h-partners.com",
    description="Tune MCP Service",
    packages=find_packages(where="."),
    include_package_data=True,
    data_files=data_files,
    entry_points={
        "console_scripts": [
            "tune-openapi = src.start_workflow:main",
            "tune-mcpserver = src.start_mcpserver:main",
            "euler-copilot-tune = src.start_tune:main",
        ],
    },
    install_requires=[
        # "faiss_cpu",
        "fastapi",
        "numpy",
        "openai",
        "paramiko",
        "pydantic>=2.8.2",
        "PyYAML",
        "scikit_learn",
        "tqdm",
        "uvicorn",
        # "zhipuai",
        "requests",
        "langchain",
        "langchain-openai",
        "email-validator",
        "httpx",
        "tabulate",
        # "pyfiglet",
        "gssapi",
        "pandas",
        "mcp==1.6.0"
    ],
    url="https://gitee.com/openeuler/A-Tune/tree/euler-copilot-tune/"
)
