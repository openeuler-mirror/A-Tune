from typing import Any


class ExecuteResult:
    def __init__(self, status_code: int = -1, output: Any = None, err_msg: str = ""):
        self.status_code = status_code
        self.output = output
        self.err_msg = err_msg

    def __dict__(self):
        return {
            "status_code": self.status_code,
            "err_msg": self.err_msg,
            "output": self.output,
        }

    def __repr__(self):
        return str(self.__dict__())
