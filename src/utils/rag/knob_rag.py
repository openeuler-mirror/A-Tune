import json
import logging
import os
import pickle
import re
from typing import Any, Dict, Tuple

import faiss
import numpy as np
from sklearn.preprocessing import normalize
from tqdm import tqdm

from src.utils.llm import get_llm_response, get_embedding

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class KnobRag:
    def __init__(self, config_path: str, bottle_neck: str, application: str, system_report: str):
        self.bottle_neck = bottle_neck
        self.application = application
        self.system_report = system_report
        self.config = self.load_config(config_path)
        self.topk: int = self.config.get("topk", 10)
        self.threshold: float = self.config.get("threshold", 0.5)

    def load_config(
            self,
            config_path: str
    ) -> Dict[str, Any]:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            logging.error(f"配置文件 {config_path} 未找到。")
            raise Exception(f"配置文件 {config_path} 未找到。")
        except json.JSONDecodeError:
            logging.error(f"配置文件 {config_path} 格式错误。")
            raise Exception(f"配置文件 {config_path} 格式错误。")

    def get_query_list(
            self,
    ) -> list:
        #         prompt = f"""
        # 你是一个经验丰富的linux故障分析专家，你的任务是根据给定的系统分析报告，分析出当前系统存在的问题。
        # 根据系统分析报告给出的结果，你需要做如下两件事情：
        # 1.分析系统报告，根据系统报告判断哪些方面有问题，描述该问题可能产生的原因
        # 2.输出有问题的情况，针对没有潜在问题和性能瓶颈的方面请不要输出，包括对系统的建议也不要输出
        # 分析的结果用list格式输出，严格按照一行一个结果的格式，以数字开头，不要添加额外的输入语句，不要换行，一条问题写一行，每条结果前面加上数字编号后面跟上输出结果。
        # 请注意仅仅只输出系统中有问题的指标，如果该场景没有问题也没有明显瓶颈，就不要输出在结果中，另外针对系统的建议也不需要输出。
        # 系统分析报告是：{self.system_report}
        #         """
        prompt = f"""
        # CONTEXT # 
        当前linux系统性能分析报告是:
        {self.system_report}

        # OBJECTIVE #
        请根据给定的系统性能分析报告,分析出当前系统存在的性能问题。
        要求：
        1.分析系统报告，根据系统报告判断哪些方面有问题，描述该问题可能产生的原因
        2.输出有问题的情况，针对没有潜在问题和性能瓶颈的方面请不要输出，包括对系统的建议也不要输出

        # STYLE #
        你是一个经验丰富的linux故障分析专家,你的回答应该逻辑严谨、表述客观、简洁易懂、条理清晰

        # Tone #
        你应该尽可能秉承严肃、认真、严谨的态度

        # AUDIENCE #
        你的答案将会是其他系统运维专家的重要参考意见，请尽可能提供真实有用的信息，不要胡编乱造。

        # RESPONSE FORMAT #
        分析的结果用list格式输出,严格按照一行一个结果的格式,以数字开头,不要添加额外的输入语句,不要换行,一条问题写一行,每条结果前面加上数字编号后面跟上输出结果。

        """

        response = get_llm_response(prompt)
        pattern = r"^\s*[\d\.|-].*"
        matches = re.findall(pattern, response, re.MULTILINE)
        return matches if matches else []

    # 构建索引
    def build_index(
            self,
            file_name: str,
    ) -> Tuple[faiss.IndexFlatIP, list]:
        docs = []
        # with open(f"{file_name}.jsonl", "r", encoding="utf-8") as f:
        current_file_path = os.path.abspath(__file__)
        current_dir_path = os.path.dirname(current_file_path)
        file_name = f"{file_name}.jsonl"
        config_path = os.path.join(current_dir_path, '..', '..', 'knowledge_base', 'optimize', 'parameter', file_name)
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f.readlines():
                docs.append(json.loads(line))

        index_path = f"{file_name}_index.pkl"
        if os.path.exists(index_path):
            print(f"Detect cached index, read index from {index_path} ...")
            with open(index_path, 'rb') as file:
                index = pickle.load(file)
            print(type(index), type(docs))
            return index, docs

        embeddings = []
        for doc in tqdm(docs, desc=f"Building index for {file_name}..."):
            query_embedding = get_embedding(doc["content"])
            embeddings.append(query_embedding)
        normalized_embeddings = normalize(np.array(embeddings).astype('float32'))
        d = len(embeddings[0])
        index = faiss.IndexFlatIP(d)
        index.add(normalized_embeddings)

        with open(index_path, 'wb') as file:
            pickle.dump(index, file)

        print(type(index), type(docs))

        return index, docs

    # 召回top5且阈值大于0.6的样本
    # 返回值类型？
    def retrieve(
            self,
            index: faiss.Index,
            docs: list,
            query_list: list,
    ) -> list:
        result = {}
        unique = set()

        for query_data in query_list:
            query_embedding = get_embedding(query_data)
            D, I = index.search(normalize(np.array(query_embedding).astype('float32').reshape(1, -1)), self.topk)

            for idx, score in zip(I[0], D[0]):
                if score > self.threshold:
                    if idx not in unique:
                        result[idx] = score
                    result[idx] = max(result[idx], score)
        result = [docs[item[0]] for item in sorted(list(result.items()), key=lambda x: x[1], reverse=True)]
        print(type(result[:self.topk]))
        return result[:self.topk]

    def run(self) -> list:
        query_list = self.get_query_list()
        if self.bottle_neck.lower() == "cpu":
            query_list.append("CPU密集型任务")
        if not query_list:
            return []
        print("query is :{}".format(query_list))

        # 分系统和应用两组分别召回前5个匹配的参数
        system_index, system_docs = self.build_index("system")
        system_result = self.retrieve(system_index, system_docs, query_list)
        if self.application.lower() != "none":
            self.application = self.application.lower()
            application_index, application_docs = self.build_index(self.application)
            application_result = self.retrieve(application_index, application_docs, query_list)
        else:
            application_result = []
        final_result = system_result + application_result
        return [x["param_name"] for x in final_result]

# if __name__ == "__main__":
#     system_report = """一、CPU性能分析

# 1. 负载分析：过去1分钟内系统负载迅速增加，表明系统对CPU性能的需求可能提高。而过去10分钟内负载稳定，但呈上升趋势，这进一步证实了未来可能对CPU性能的需求会上升。

# 2. CPU利用率：当前系统用户态和内核态CPU利用率分别为0.0和0.0002，总体利用率为0.00019999999999997797。这表明CPU利用率非常低，系统在CPU方面没有明显的性能瓶颈。

# 二、内存性能分析

# 系统内存使用率为0.0288，总体来说内存使用较为充足。然而，系统可用交换空间为0.0，低于预设阈值。这表明系统可能很快会耗尽虚拟内存，需要减少运行程序的数量和大小，或增加交换空间来避免内存不足的问题。

# 三、网络I/O性能分析

# 1. 网络流量：平均每秒接收和发送数据包分别为5.00和1.00，主要来自ens3接口。接收和发送的数据量较低，分别为0.86KB和0.05KB。

# 2. 接口利用率：所有接口利用率均为0.00，说明网络接口未达到性能瓶颈。

# 综上，网络I/O性能良好，未对系统性能产生显著影响。

# 四、磁盘性能分析

# 1. 磁盘I/O：系统iowait值为0.0，表明磁盘I/O未导致进程等待。

# 2. 磁盘利用率：所有磁盘利用率均为0.0，说明磁盘使用率极低，磁盘I/O不是系统性能的瓶颈。

# 综合分析：

# 1. 根据已知信息，系统性能瓶颈点为disk I/O，但根据我们的分析，磁盘性能指标显示磁盘I/O并没有对系统性能产生显著影响。

# 2. CPU和内存利用率较低，网络性能良好，这些维度的性能指标均未达到瓶颈。

# 3. 建议关注内存可用交换空间，可能需要增加交换空间或调整运行程序以避免内存不足。

# 4. 考虑到过去1分钟系统负载迅速增加，建议进一步观察系统负载变化，以便对CPU性能需求进行更准确的评估。

# 本报告基于当前采集的系统指标进行分析，如有需要，请持续关注系统性能变化，以便及时调整优化措施。"""
#     # config_path = Path('src')/'knowledge_base' / 'optimize' / 'parameter' / 'mysql.jsonl'
#     config_path = r"D:\github\tuning\src\utils\rag\rag_config.json"
#     rag = KnobRag(config_path=config_path, bottle_neck="CPU", application="mysql", system_report=system_report)
#     ret = rag.run()
# print(ret)
# ret=['vm.swappiness', 'vm.min_free_kbytes', 'vm.dirty_expire_centisecs', 'vm.overcommit_ratio', 'vm.dirty_background_ratio', 'vm.dirty_bytes', 'vm.dirty_background_bytes', 'kernel.shmmax', 'kernel.shmall', 'vm.drop_caches']
