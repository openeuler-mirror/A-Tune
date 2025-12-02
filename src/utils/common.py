
from typing import List, Any, Union
from tabulate import tabulate
from wcwidth import wcswidth
from src.config import config

def language():
    if config["language"] == "zh":
        return "zh"
    else:
        return "en"

def translate(chinese, english):
    if language() == "zh":
        return chinese
    else:
        return english

def display_banner():
    try:
        import pyfiglet
        banner = pyfiglet.figlet_format("EulerCopilot v1.0", font="slant")
        print(banner)
    except ImportError:
        print("EulerCopilot v1.0 \n")


def truncate_string(s, max_length=30):
    """
    截断字符串，如果超过指定长度则在末尾加上...
    """
    s = str(s)
    if len(s) > max_length:
        return s[: max_length - 3] + "..."
    return s


def flatten_dict(d, parent_key=None):
    """
    递归地将嵌套字典扁平化，键路径以 list[str] 形式存储
    """
    items = []
    if parent_key is None:
        parent_key = []
    for k, v in d.items():
        new_key = parent_key + [k]  # 将当前键添加到路径列表中
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key))  # 递归处理嵌套字典
        else:
            items.append((new_key, v))  # 保存键路径和值
    return items


def preview_data(data: dict, preview_nums: int = 5):
    """
    将扁平化的字典转换为列表，每个元素是一个元组
    """
    flattened = flatten_dict(data)
    if len(flattened) > 2 * preview_nums:
        # 确定省略号部分的键路径长度
        ellipsis_list = ["..."] * len(flattened[0][0])
        flattened = (
            flattened[:preview_nums]
            + [(ellipsis_list, "...")]
            + flattened[-preview_nums:]
        )
    result = []
    for key_list, value in flattened:
        # 将键路径和值都转换为字符串并截断
        truncated_keys = [truncate_string(k) for k in key_list]
        truncated_value = truncate_string(value)
        result.append(truncated_keys + [truncated_value])  # 将键路径和值组合成一个列表
    return result

def cn_tabulate(
    data: List[List[Any]],
    headers: Union[List[str], str] = (),
    tablefmt: str = "grid",
    **kwargs
) -> str:
    if not data:
        return tabulate([], headers=headers, tablefmt=tablefmt, **kwargs)

    if headers == "keys" and isinstance(data[0], dict):
        keys = list(data[0].keys())
        data = [[row.get(k, "") for k in keys] for row in data]
        headers = keys
    elif isinstance(headers, list) and isinstance(data[0], dict):
        data = [[row.get(k, "") for k in headers] for row in data]

    max_cols = max(len(row) for row in data)
    if headers:
        max_cols = max(max_cols, len(headers))

    col_widths = []
    for col in range(max_cols):
        max_width = 0
        if headers and col < len(headers):
            max_width = wcswidth(str(headers[col]))
        for row in data:
            if col < len(row):
                max_width = max(max_width, wcswidth(str(row[col])))
        col_widths.append(max_width)

    def pad_cell(s, width):
        s = str(s)
        pad_len = width - wcswidth(s)
        return s + " " * pad_len

    padded_data = [
        [pad_cell(row[col], col_widths[col]) if col < len(row) else " " * col_widths[col]
         for col in range(max_cols)]
        for row in data
    ]
    padded_headers = (
        [pad_cell(headers[col], col_widths[col]) if col < len(headers) else " " * col_widths[col]
         for col in range(max_cols)]
        if headers else ()
    )

    return tabulate(padded_data, headers=padded_headers, tablefmt=tablefmt, **kwargs)

def display_metrics(
    metric_data: dict,
    headers: list[str] = ["metric_name", "metric_value"],
    title: str = "",
    preview_nums: int = 5,
):
    if not isinstance(metric_data, dict):
        raise TypeError(f"display metric_data only support dict data now!")

    table_str = cn_tabulate(
        preview_data(metric_data),
        headers=headers,
        tablefmt="grid",
    )
    display_content = "\n".join([title, table_str])
    print(display_content)

class ExecuteResult:
    def __init__(self, status_code: int = -1, output: str = "", err_msg: str = ""):
        self.status_code = status_code
        self.output = output
        self.err_msg = err_msg

    def __repr__(self):
        return str({
            "status_code": self.status_code,
            "output": self.output,
            "err_msg": self.err_msg,
        })
