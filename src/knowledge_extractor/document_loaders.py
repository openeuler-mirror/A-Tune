import pandas as pd
import numpy as np
import re
import fitz  # PyMuPDF
from docx import Document

# 判断是否为数字
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# 判断是否为英文
def is_english(s):
    return bool(re.match(r'^[a-zA-Z0-9_]+$', str(s)))

# 判断是否为中文
def is_chinese(s):
    return bool(re.match(r'^[\u4e00-\u9fff]+$', str(s)))

# 分析数据类型
def analyze_data_types(df):
    row_types = []
    col_types = []

    # 分析每行的数据类型
    for i in range(len(df)):
        row_type = set()
        for value in df.iloc[i]:
            if pd.isna(value):
                continue
            if is_number(value):
                row_type.add('number')
            elif is_english(value):
                row_type.add('english')
            elif is_chinese(value):
                row_type.add('chinese')
            else:
                row_type.add('string')
        row_types.append(row_type)

    # 分析每列的数据类型
    for j in range(len(df.columns)):
        col_type = set()
        for value in df.iloc[:, j]:
            if pd.isna(value):
                continue
            if is_number(value):
                col_type.add('number')
            elif is_english(value):
                col_type.add('english')
            elif is_chinese(value):
                col_type.add('chinese')
            else:
                col_type.add('string')
        col_types.append(col_type)

    return row_types, col_types

# 计算行之间的相似度
def calculate_row_similarity(row_types):
    similarities = []
    for i in range(len(row_types)):
        row_similarities = []
        for j in range(len(row_types)):
            if i != j:
                sim = len(row_types[i].intersection(row_types[j])) / len(row_types[i].union(row_types[j]))
                row_similarities.append(sim)
            else:
                row_similarities.append(1)  # 自身相似度为1
        similarities.append(row_similarities)
    return similarities

# 计算列之间的相似度
def calculate_column_similarity(col_types):
    similarities = []
    for i in range(len(col_types)):
        col_similarities = []
        for j in range(len(col_types)):
            if i != j:
                sim = len(col_types[i].intersection(col_types[j])) / len(col_types[i].union(col_types[j]))
                col_similarities.append(sim)
            else:
                col_similarities.append(1)  # 自身相似度为1
        similarities.append(col_similarities)
    return similarities

# 判断数据排列方式并输出结构化数据到文本文件
def excel2text(file_path, sheet_name='Sheet1', output_file='../mysql_knowledge/temp/excel_out.txt'):
    # 读取Excel文件
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    # 分析数据类型
    row_types, col_types = analyze_data_types(df)

    # 计算行之间的相似度
    row_similarities = calculate_row_similarity(row_types)
    row_avg_similarity = np.mean(row_similarities)

    # 计算列之间的相似度
    col_similarities = calculate_column_similarity(col_types)
    col_avg_similarity = np.mean(col_similarities)

    # 判断排列方式
    if row_avg_similarity > col_avg_similarity:
        orientation = "横向分布"
    else:
        orientation = "纵向分布"

    # 打开输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        # 根据排列方式输出结构化数据
        if orientation == "横向分布":
            # 读取Excel文件，指定标题行
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
            for index, row in df.iterrows():
                for column in df.columns:
                    f.write(f"{column}: {row[column]}\n")
                f.write("-" * 40 + "\n")
        else:
            # 读取Excel文件，不指定标题行
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            df_transposed = df.T
            for index, row in df_transposed.iterrows():
                for column in df_transposed.columns:
                    f.write(f"{row[0]}: {row[column]}\n")
                f.write("-" * 40 + "\n")

def pdf2text(pdf_path, output_file='../mysql_knowledge/temp/pdf_out.txt'):
    # 打开PDF文件
    doc = fitz.open(pdf_path)
    
    # 打开输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        # 遍历PDF的每一页
        for page_number in range(len(doc)):
            page = doc.load_page(page_number)  # 加载当前页
            page_text = page.get_text()  # 提取当前页的文本
            
            # 将当前页的文本写入文件
            f.write(f"Page {page_number + 1}:\n")
            f.write(page_text)
            f.write("\n\n")  # 添加一个空行分隔各页的文本

    # 关闭PDF文件
    doc.close()


def docx2text(docx_path, output_file='../mysql_knowledge/temp/docx_out.txt'):
    """
    提取 .docx 文件中的文本内容并保存为 .txt 文件。

    参数:
        docx_path (str): 输入的 .docx 文件路径。
        output_txt_path (str): 输出的 .txt 文件路径。
    """
    try:
        # 打开 .docx 文件
        doc = Document(docx_path)
        
        # 提取所有段落的文本
        text = "\n".join([para.text for para in doc.paragraphs])
        
        # 将文本写入 .txt 文件
        with open(output_file, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)
    except Exception as e:
        print(f"Error processing the file: {e}")

