from abc import ABC, abstractmethod
from typing import Dict, Any

from src.utils.llm import get_llm_response


class BaseAnalyzer(ABC):
    def __init__(self, app: str, data: Dict[str, Any]):
        self.data = data
        self.app = app

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
        analyze_result = self.analyze()
        report = self.generate_report(analyze_result)
        return report
