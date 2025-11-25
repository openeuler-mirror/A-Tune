from src.utils.constant import DATA_PATH

import os
import logging
import pickle
from src.config import config

enable_save_snapshot = config["feature"][0]["save_snapshot"]
enable_use_snapshot = config["feature"][0]["use_snapshot"]
snapshot_path_inited = False
snapshot_path = ""

# 初始化快照目录
if not snapshot_path_inited:
    if os.path.exists(DATA_PATH) and os.path.isdir(DATA_PATH):
        snapshot_path = os.path.join(DATA_PATH, "snapshot")
    else:
        snapshot_path = os.path.join(os.getcwd(), "data", "snapshot")
        os.mkdirs(snapshot_path, mode=0o755, exist_ok=True)
    snapshot_path_inited = True
    logging.info(f"save_snapshot: {enable_save_snapshot}; use_snapshot: {enable_use_snapshot}")
    if enable_save_snapshot or enable_use_snapshot:
        logging.info(f"snapshot_path: {snapshot_path}")

# 保存快照
def save_snapshot(var, filename: str):
    if not enable_save_snapshot:
        return
    snapshot_file_path = os.path.join(snapshot_path, f"{filename}.pickle")
    with open(snapshot_file_path, 'wb') as f:
        pickle.dump(var, f)
        logging.info(f"{filename} snapshot saved to {snapshot_file_path}")

# 加载快照
def load_snapshot(filename: str):
    if not enable_use_snapshot:
        return None
    try:
        snapshot_file_path = os.path.join(snapshot_path, f"{filename}.pickle")
        with open(snapshot_file_path, 'rb') as f:
            var = pickle.load(f)
            logging.info(f"{filename} snapshot loaded from {snapshot_file_path}")
            return var
    except FileNotFoundError:
        return None