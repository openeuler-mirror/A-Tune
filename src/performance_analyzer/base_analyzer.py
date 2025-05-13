from src.utils.llm import get_llm_response
from typing import Dict, Any
from abc import ABC, abstractmethod


class BaseAnalyzer(ABC):
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    @abstractmethod
    def analyze(self, **kwargs) -> str:
        pass
    
    @abstractmethod
    def generate_report(self, **kwargs) -> str:
        pass

    def ask_llm(
        self, 
        prompt: str
    ) -> str:
        return get_llm_response(prompt)
    
    def generate_report_line(
        self,
        condition: Any,
        message: str,
    ) -> str:
        if condition:
            return message + "\n"
        return ""

    def run(self) -> str:
        analyze_result= self.analyze()
        report = self.generate_report(analyze_result)
        return report
