from text_split import *
from web_crawler import *
from api_server import *
from save_knowledge import *
from code_extractor import *
from document_loaders import *
from merge_files import *
from output import *
import yaml
import os
import time

def load_config(file_path: str) -> dict:
    """
    加载配置文件。

    Parameters:
        file_path (str): 配置文件路径。

    Returns:
        dict: 配置信息。
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config


def pipeline(param: str, app: str, config: dict) -> None:
    """
    处理多来源参数知识并汇总生成知识库内容。

    Parameters:
        param (str): 参数名称。
        app (str): 应用程序名称。
        config (dict): 配置信息。

    Returns:
        None
    """
    save_path = config.get("save_path", "../{}_knowledge/".format(app))  # 存储文件的路径
    output_dir = save_path + "summary/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    official_doc_path = save_path + "official/" + param + ".json"
    gpt_suggestion_path = save_path + "gpt/" + param + ".json"
    web_suggestion_path = save_path + "web/" + param + ".json"
    official_doc = ""
    gpt_suggestion = ""
    web_suggestion = ""

    try:
        with open(official_doc_path, 'r', encoding='utf-8') as file:
            official_doc = file.read()
            print(official_doc)
    except FileNotFoundError:
        print("官方文档文件未找到，已设置为空。")

    try:
        with open(gpt_suggestion_path, 'r', encoding='utf-8') as file:
            gpt_suggestion = file.read()
            print(gpt_suggestion)
    except FileNotFoundError:
        print("GPT建议文件未找到，已设置为空。")

    try:
        with open(web_suggestion_path, 'r', encoding='utf-8') as file:
            web_suggestion = file.read()
            print(web_suggestion)
    except FileNotFoundError:
        print("WEB建议文件未找到，已设置为空。")

    # 总结官方文档及gpt和web建议
    sources_json = aggregate_result(param, official_doc, web_suggestion, gpt_suggestion, app)

    try:
        json_data = json.loads(sources_json)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误：{e}")
    with open(save_path + "summary/" + param + ".json", 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)


def main(config_file_path: str) -> None:
    """
    主函数，负责执行整个知识库生成流程。

    Parameters:
        config_file_path (str): 配置文件路径。

    Returns:
        None
    """
    config = load_config(config_file_path)
    app = config.get("app_name", "mysql")
    params_file = config.get("params_file", "")
    save_path = config.get("save_path", "../{}_knowledge/".format(app))

    start_time = time.perf_counter()

    STEP = "======  {}  ======"

    # step 1: 参数列表读取
    if config.get("step1", False):
        print(STEP.format("步骤 1: 读取参数列表"))
        if os.path.exists(params_file):
            with open(params_file, 'r', encoding='utf-8') as f:
                params = f.read()
            params = [param.strip('"') for param in params.split()]
            print(params)
            time.sleep(2)
        else:
            print("提示：参数文件不存在，将提取官方文档中所有参数")
            params = []
    else:
        print(STEP.format("步骤 1: 跳过"))

    # step 2: official信息读取并存储文本
    if config.get("step2", False):
        print(STEP.format("步骤 2: official信息读取并存储"))
        urls = config.get("official_url",[])
        os.makedirs(save_path, exist_ok=True)
        output_file = save_path + "official_text.txt"
        for url in urls:
            print(url)
            convert_html_to_markdown(url,output_file)
        time.sleep(2)
    else:
        print(STEP.format("步骤 2: 跳过"))

    # step 3: web信息读取并存储文本
    if config.get("step3", False):
        print(STEP.format("步骤 3: web信息读取并存储"))
        web_list = config.get("web_url",[])
        for web in web_list:
            output_file = save_path + "web_text.txt"
            convert_html_to_markdown(web,output_file)
        time.sleep(2)
    else:
        print(STEP.format("步骤 3: 跳过"))

    # step 4: official信息转化为结构化数据（所有参数）
    if config.get("step4", False):
        print(STEP.format("步骤 4: official信息转化为结构化数据"))
        # 进行滑窗划分和gpt提取知识，生成结构化数据
        with open(save_path+"official_text.txt", 'r', encoding='utf-8') as f:
            text = f.read()
        #找到最长的段落，将滑窗的滑动的步长设置为滑窗长度-longtext
        long_text = find_longest_paragraph_length(text)
        if long_text > 1000:
            long_text = 1000
        elif long_text < 300:
            long_text = 300
        window_size = config.get("window_size",5000)
        step = window_size - long_text
        # official信息的分割结果
        segments = sliding_window_split(text, window_size, step)
        for segment in segments:
            ans = parameter_official_knowledge_preparation(segment, app)
            split_json_to_files(ans, save_path+"official")
        time.sleep(2)
    else:
        print(STEP.format("步骤 4: 跳过"))
    if len(params)==0:
        for filename in os.listdir(save_path+"official"):
            if filename.endswith(".json"):
                params.append(filename[:-5])
    print(params)

    # step 5: web信息转化为分条的参数信息（根据给定参数列表）
    if config.get("step5", False):
        print(STEP.format("步骤 5: web信息转化为结构化数据"))
        # web信息提取 信息已存在web_text.txt中
        with open(save_path + "web_text.txt", 'r', encoding='utf-8') as f:
            text = f.read()
        if not os.path.exists(save_path + "web/"):
            os.makedirs(save_path + "web/")
        #找到最长的段落，将滑窗的滑动的步长设置为滑窗长度-longtext
        long_text = find_longest_paragraph_length(text)
        if long_text > 1000:
            long_text = 1000
        elif long_text < 300:
            long_text = 300
        window_size = config.get("window_size",5000)
        step = window_size - long_text
        segments = sliding_window_split(text, window_size, step)
        ans_list = []
        for segment in segments:
            ans = parameter_knowledge_preparation(segment, params, app)
            if ans is None:
                continue
            try:
                ans_list.append(json.loads(ans))
            except json.JSONDecodeError as e:
                print(f"JSON解析错误：{e}")
        for param in params:
            web_text = ""
            for ans in ans_list:
                for item in ans:
                    if item["name"] == param:
                        web_text += str(item) + "\n"
            if web_text != "":
                ans = aggregate_web_result(web_text,param,app)
                try:
                    json_data = json.loads(ans)
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误：{e}")
                with open(save_path + "web/"+param+".json", 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, indent=4, ensure_ascii=False)
        time.sleep(2)
    else:
        print(STEP.format("步骤 5: 跳过"))

    # step 6: 从源代码中获取参数知识
    if config.get("step6", False):
        print(STEP.format("步骤 6: 从源代码中获取参数知识"))
        folder = config.get("code_path","../code")
        out_file = save_path + "code_text.txt"
        # 提取代码片段
        extract_code_snippets(params, folder,out_file)
        #  code信息已存在code_text.txt中
        with open(save_path + "code_text.txt", 'r', encoding='utf-8') as f:
            text = f.read()
        if not os.path.exists(save_path + "code/"):
            os.makedirs(save_path + "code/")
        #找到最长的段落，将滑窗的滑动的步长设置为滑窗长度-longtext
        long_text = find_longest_paragraph_length(text)
        if long_text > 1000:
            long_text = 1000
        elif long_text < 300:
            long_text = 300
        window_size = config.get("window_size",5000)
        step = window_size - long_text
        segments = sliding_window_split(text, window_size, step)
        ans_list = []
        for segment in segments:
            ans = parameter_knowledge_preparation(segment, params, app)
            if ans is None:
                continue
            try:
                ans_list.append(json.loads(ans))
            except json.JSONDecodeError as e:
                print(f"JSON解析错误：{e}")
        for param in params:
            web_text = ""
            for ans in ans_list:
                for item in ans:
                    if item["name"] == param:
                        web_text += str(item) + "\n"
            if web_text != "":
                ans = aggregate_web_result(web_text,param,app)
                try:
                    json_data = json.loads(ans)
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误：{e}")
                with open(save_path + "code/"+param+".json", 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, indent=4, ensure_ascii=False)
        time.sleep(2)
    else:
        print(STEP.format("步骤 6: 跳过"))

    # step 7: GPT直接生成结构化数据
    if config.get("step7", False):
        print(STEP.format("步骤 7: GPT直接生成结构化数据"))
        # gpt数据获取
        batch_size = 15  # 每批次处理15个元素
        for i in range(0, len(params), batch_size):      # 按批次循环处理
            batch_params = params[i:i+batch_size]  # 提取当前批次
            gpt_data = get_gpt_knowledge(batch_params,app)
            split_json_to_files(gpt_data, save_path + "gpt")
        time.sleep(2)
    else:
        print(STEP.format("步骤 7: 跳过"))

    # step 8: 通过补充文件作为补充的参数信息输入。
    if config.get("step8", False):
        print(STEP.format("步骤 8: 通过补充文件作为补充的参数信息输入"))
        append_file_paths = config.get("append_file_paths",[])
        # 根据文件类型进行处理
        for file_path in append_file_paths:
            # 获取文件扩展名并转换为小写
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()

            # 判断文件类型
            if file_extension == ".pdf":
                pdf2text(file_path, save_path+"temp/pdf_out.txt")
                with open(save_path+"temp/pdf_out.txt", 'r', encoding='utf-8') as f:
                    text = f.read()
            elif file_extension == ".docx":
                docx2text(file_path, save_path+"temp/docx_out.txt")
                with open(save_path+"temp/docx_out.txt", 'r', encoding='utf-8') as f:
                    text = f.read()
            elif file_extension in [".xlsx", ".xls"]:
                excel2text(file_path, "Sheet1", save_path+"temp/excel_out.txt")
                with open(save_path+"temp/excel_out.txt", 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                print("Unsupported File Type")
                continue
            
            if(len(text) < config.get("window_size",5000)):
                ans = parameter_official_knowledge_preparation(segment)
                split_json_to_files(ans, save_path+"addition")
            else:
                long_text = find_longest_paragraph_length(text)
                if long_text > 1000:
                    long_text = 1000
                window_size = config.get("window_size",5000)
                step = window_size - long_text
                # 文档补充信息的分割结果
                segments = sliding_window_split(text, window_size, step)
                for segment in segments:
                    ans = parameter_official_knowledge_preparation(segment)
                    split_json_to_files(ans, save_path+"addition")
        time.sleep(2)
    else:
        print(STEP.format("步骤 8: 跳过"))

    # step 9: 结构化数据的信息聚合
    if config.get("step9", False):
        print(STEP.format("步骤 9: 结构化数据的信息聚合"))
        time.sleep(2)
        for param in params:
            pipeline(param, app, config)
    else:
        print(STEP.format("步骤 9: 跳过"))

    # step 10: 生成参数知识库总文件
    if config.get("step10", False):
        print(STEP.format("步骤 10: 生成参数知识库总文件"))
        time.sleep(2)
        # # 合并json
        input_directory = save_path+"summary"  # 替换为包含JSON文件的目录路径
        output_file = save_path+ app+ "_param.json"     # 替换为输出文件的路径
        merge_json_files(input_directory, output_file)
        output_file_json = save_path+ app+ ".json"     # 替换为输出文件的路径
        process_json(output_file, output_file_json)

        # # json转换为jsonl
        # input_file = save_path+ app+ "_param.json"
        # output_file = save_path+ app+ "_param.jsonl"
        # json_to_jsonl(input_file, output_file)
    else:
        print(STEP.format("步骤 10: 跳过"))
    

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"生成的参数知识库内容：{params}")
    print("-----------------------")
    print(f"程序执行时间：{execution_time} 秒")
    print(f"一共生成了参数知识：{len(params)} 条")

if __name__ == "__main__":

    config_file_path = "config/app_config.yaml"
    main(config_file_path)