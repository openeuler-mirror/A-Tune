import jieba
import re

def is_chinese(text):
    """
    判断文本是否为中文（如果包含非中文字符则返回False）

    Parameters:
        text (str): 输入文本

    Returns:
        bool: 如果文本全为中文字符，返回True；否则返回False
    """
    return all('\u4e00' <= char <= '\u9fff' for char in text)


def split_text_into_segments(text: str, max_length: int = 5000) -> list:
    """
    将文本分割成多个段落，每个段落不超过max_length字符，并尽量保留语义完整性。
    中文段落使用jieba分词，英文段落直接输出。

    Parameters:
        text (str): 输入文本
        max_length (int): 每个段落的最大字符数，默认为5000

    Returns:
        list: 分割后的文本段落列表
    """
    paragraphs = text.split('\n')  # 按行分段
    segments = []
    current_segment = ""
    
    for para in paragraphs:
        if len(current_segment) + len(para) + 1 <= max_length:
            # 如果当前段落加上新段落不超过最大字符数，就加入当前段落
            if current_segment:
                current_segment += '\n' + para
            else:
                current_segment = para
        else:
            # 当前段落超过限制，保存并重新开始一个新的段落
            segments.append(current_segment)
            current_segment = para
    
    # 添加最后一个段落
    if current_segment:
        segments.append(current_segment)
    
    return segments


def tokenize_text(text: str) -> str:
    """
    对中文文本进行分词，英文文本保持原样

    Parameters:
        text (str): 输入文本

    Returns:
        str: 分词后的文本（中文）或原样文本（英文）
    """
    if is_chinese(text):
        # 中文段落进行jieba分词
        words = jieba.cut(text)
        return " ".join(words)
    else:
        # 英文段落保持原样输出
        return text


def process_text_file(input_file: str, output_prefix: str, max_length: int = 5000):
    """
    处理文本文件，进行分段和分词，并输出为多个文件。
    中文段落分词，英文段落保持原样输出

    Parameters:
        input_file (str): 输入文件路径
        output_prefix (str): 输出文件前缀
        max_length (int): 每个段落的最大字符数，默认为5000
    """
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 将文本分割成多个段落
    segments = split_text_into_segments(text, max_length)
    
    # 输出分词后的段落到多个文件
    for i, segment in enumerate(segments):
        tokenized_text = tokenize_text(segment)
        output_file = f"{output_prefix}_{i + 1}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(tokenized_text)
        print(f"文件 {output_file} 已创建，包含 {len(segment)} 字符。")


def sliding_window_split(text: str, window_size: int, step: int) -> list:
    """
    使用滑动窗口对文本进行分割。

    Parameters:
        text (str): 待分割的文本
        window_size (int): 窗口大小，即每个分割片段的字符数
        step (int): 滑动窗口的步长

    Returns:
        list: 分割后的文本片段列表

    Raises:
        ValueError: 如果窗口大小或步长不大于0，或者步长大于窗口大小
    """
    if window_size <= 0 or step <= 0:
        raise ValueError("窗口大小和步长必须为正整数")

    if window_size > len(text):
        return [text]  # 或者返回空列表 []

    if step > window_size:
        raise ValueError("步长不能大于窗口大小")

    # 初始化一个空列表来存储分割后的文本片段
    segments = []

    # 使用滑动窗口进行文本分割
    for i in range(0, len(text) - window_size + 1, step):
        # 提取当前窗口内的文本片段
        segment = text[i:i + window_size]
        # 将文本片段添加到列表中
        segments.append(segment)

    # 检查是否还有剩余的文本
    if len(text) % step != 0:
        segments.append(text[-window_size:])

    return segments

def find_longest_paragraph_length(text: str, delimiter: str = '\n') -> int:
    """
    找出文本中最长段落的长度

    Parameters:
        text (str): 输入文本
        delimiter (str): 段落分隔符，默认为换行符

    Returns:
        int: 最长段落的长度
    """
    # 根据段落分隔符分割文本
    if delimiter == '\n':
        paragraphs = text.split(delimiter)
    else:
        paragraphs = re.split(delimiter, text)
    
    # 计算每个段落的长度
    paragraph_lengths = [len(paragraph) for paragraph in paragraphs]
    
    # 找出最长段落的长度
    max_paragraph_length = max(paragraph_lengths)
    
    return max_paragraph_length