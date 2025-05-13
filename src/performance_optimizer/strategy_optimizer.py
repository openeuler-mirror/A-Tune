import json
import logging
from typing import List, Dict, Optional, Tuple

from .base_optimizer import BaseOptimizer
from src.utils.llm import get_llm_response

knowledge_base_path = "./src/knowledge_base/optimize/strategy/system.jsonl"

class StrategyOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        """
        初始化性能优化推荐器
        
        参数:
            knowledge_base_path: 策略知识库JSON文件路径
        """
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        
    def _load_knowledge_base(self, file_path: str) -> List[Dict]:
        """加载策略知识库JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"知识库文件 {file_path} 未找到")
        except json.JSONDecodeError:
            raise ValueError(f"知识库文件 {file_path} 不是有效的JSON格式")
    
    def _filter_strategies(self, bottleneck: str) -> List[Dict]:
        """
        根据瓶颈点过滤策略
        
        参数:
            bottleneck: 系统性能瓶颈点，可能值为[CPU, DISK, NETWORK, MEMORY, NONE]
            
        返回:
            匹配的策略列表
        """
        if bottleneck == "NONE":
            return []
            
        return [strategy for strategy in self.knowledge_base 
                if strategy["对应瓶颈点"].startswith(bottleneck)]
    
    def _generate_llm_prompt(self, strategies: List[Dict], bottleneck: str, 
                           business_context: Optional[str] = None) -> str:
        """
        生成LLM提示词
        
        参数:
            strategies: 候选策略列表
            bottleneck: 系统性能瓶颈点
            business_context: 当前业务场景描述
            
        返回:
            构造好的LLM提示词
        """
        strategies_info = "\n\n".join(
            f"策略 {idx + 1}:\n"
            f"名称: {s['策略名称']}\n"
            f"瓶颈点: {s['对应瓶颈点']}\n"
            f"功能说明: {s['功能说明']}\n"
            f"使用风险: {s['使用风险']}\n"
            f"是否可配置: {s['策略是否可配置']}"
            for idx, s in enumerate(strategies)
        )
        
        prompt = (
            f"当前系统性能瓶颈点为: {bottleneck}\n"
            f"{'当前业务场景为: ' + business_context if business_context else ''}\n\n"
            f"以下是候选的优化策略:\n{strategies_info}\n\n"
            "请根据以下标准评估并推荐top K条最优策略:\n"
            "1. 策略与瓶颈点的匹配程度\n"
            "2. 策略在当前业务场景下的适用性\n"
            "3. 策略的风险与收益比\n"
            "4. 策略的可配置性和易用性\n\n"
            "请直接返回策略编号(如'策略1,策略3,策略5'),不需要解释原因。"
        )
        
        return prompt
    
    def recommend_strategies(self, bottleneck: str, top_k: int = 3, 
                            business_context: Optional[str] = None) -> List[Dict]:
        """
        推荐优化策略
        
        参数:
            bottleneck: 系统性能瓶颈点
            top_k: 返回的推荐策略数量
            business_context: 当前业务场景描述
            
        返回:
            推荐的策略列表(JSON格式)
        """
        # 1. 过滤出相关策略
        candidate_strategies = self._filter_strategies(bottleneck)
        logging.info(f">>> 过滤大类瓶颈后的策略数量：{len(candidate_strategies)}")
        
        if not candidate_strategies:
            return []
        
        # 2. 生成LLM提示词并获取响应
        logging.info(f">>> 根据策略功能说明，匹配合适top K策略：")
        prompt = self._generate_llm_prompt(candidate_strategies, bottleneck, business_context)
        llm_response = get_llm_response(prompt)
        
        # 3. 解析LLM响应
        try:
            selected_indices = []
            for part in llm_response.split(','):
                part = part.strip()
                if part.startswith('策略'):
                    selected_indices.append(int(part[2:]) - 1)
                elif part.isdigit():
                    selected_indices.append(int(part) - 1)
            
            # 确保索引在有效范围内
            selected_indices = [idx for idx in selected_indices 
                              if 0 <= idx < len(candidate_strategies)]
            
            # 如果LLM返回的推荐不足top_k，补充剩余的策略
            if len(selected_indices) < top_k:
                remaining_indices = [i for i in range(len(candidate_strategies)) 
                                   if i not in selected_indices]
                selected_indices.extend(remaining_indices[:top_k - len(selected_indices)])
            
            # 取前top_k个策略
            selected_strategies = [candidate_strategies[i] for i in selected_indices[:top_k]]
            
            return selected_strategies
            
        except Exception as e:
            logging.info(f"解析LLM响应失败: {e}")
            # 如果解析失败，返回前top_k个策略
            return candidate_strategies[:top_k]
    
    def get_recommendations_json(self, bottleneck: str, top_k: int = 3,
                               business_context: Optional[str] = None) -> str:
        """
        获取JSON格式的推荐策略
        
        参数:
            bottleneck: 系统性能瓶颈点
            top_k: 返回的推荐策略数量
            business_context: 当前业务场景描述
            
        返回:
            JSON格式的推荐策略
        """
        recommendations = self.recommend_strategies(bottleneck, top_k, business_context)
        return json.dumps(recommendations, ensure_ascii=False, indent=2)

    def think(
        self,
        history: List
    ) -> Tuple[bool, str]:
        if history == []:
            self.args.bottle_neck = "CPU"
            recommendations = self.recommend_strategies(
                bottleneck=self.args.bottle_neck, 
                top_k=1,
                business_context="高并发Web服务，CPU负载主要集中在用户态处理"
            )
            logging.info(f">>> 匹配的策略数量：{len(recommendations)}")
            cmd_list = []
            for strategy in recommendations:
                logging.info(f">>> - 策略名称：{strategy['策略名称']}")
                cmd_list.append(strategy['优化步骤'])
            return False, self.get_bash_script(cmd_list)
        else:
            pass
        
    def get_bash_script(
        self, 
        cmd_list: List
    ) -> str:
        # 脚本内容的开头部分
        script_header = (
            "#!/bin/bash\n\n"
            "echo 'starting setting up strategy...'\n"
        )
        
        # 将命令列表转换为脚本中的行
        commands_str = "\n".join(cmd_list) + "\n"
        
        # 脚本内容的结尾部分
        script_footer = (
            "\necho 'set up strategy done!'\n"
        )
        
        script_content = script_header + commands_str + script_footer       
        return script_content
        
# 示例使用
if __name__ == "__main__":
    # 假设这是本地实现的LLM接口
    def get_llm_response(prompt: str) -> str:
        # 这里应该是实际调用LLM的代码
        logging.info("\nLLM提示词:\n", prompt)
        # 模拟LLM返回
        return "策略1"
    
    # 初始化优化器
    optimizer = StrategyOptimizer("./knowledge_base/optimize/strategy/system.jsonl")
    
    # 获取推荐策略
    bottleneck = "CPU"  # 输入的系统性能瓶颈点
    recommendations = optimizer.get_recommendations_json(
        bottleneck, 
        top_k=1,
        business_context="高并发Web服务，CPU负载主要集中在用户态处理"
    )
    
    logging.info("\n推荐策略:\n", recommendations)
