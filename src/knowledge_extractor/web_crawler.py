import requests
import html2text
from readability import Document


def convert_html_to_markdown(url: str, output_file_path: str) -> None:
    """
    将指定URL的HTML网页内容转换为Markdown，并保存到指定的文件中。

    Parameters:
        url (str): 目标网页的URL。
        output_file_path (str): 保存Markdown内容的文件路径。

    Returns:
        None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
    }
    # 发送HTTP GET请求获取网页内容
    response = requests.get(url, headers=headers, verify=False)
    print(response.text)

    # 检查请求是否成功
    if response.status_code == 200:
        # 获取HTML内容
        html_content = response.text
        doc = Document(html_content)
        content = doc.summary(html_partial=False)

        content = response.text
        # 创建html2text对象
        h = html2text.HTML2Text()
        
        # 配置转换器（可选）
        h.ignore_links = True  # 是否忽略链接
        h.ignore_images = True  # 是否忽略图片
        h.ignore_emphasis = True  # 是否忽略强调（如斜体、粗体）
        
        # 转换HTML为Markdown
        markdown_content = h.handle(content)
        
        # 打印Markdown内容
        print(markdown_content)
        # 将Markdown内容保存到文件中
        with open(output_file_path, 'a', encoding='utf-8') as file:
            file.write(markdown_content)

        return markdown_content
    
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print("请检查网页链接的合法性，并适当重试。")


