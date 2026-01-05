import logging
import hashlib
from datetime import datetime
import pytz
from copy import deepcopy
from src.memory.base import MemoryBase
from src.utils.llm import get_llm_response
from src.utils.prompt_instance import prompt_manager


class HierarchicalMemory(MemoryBase):
    def __init__(self, service_name):
        self.long_term_memory = ""
        self.short_term_meomry = ""
        self.history_record = []
        self.service_name = service_name

    def get(self) -> dict:
        return self.history_record[-1]

    def update(self, data: str):
        self.short_term_meomry = self._pack_short_mem(data)
        self.long_term_memory = self._pack_long_mem(data)
        self.history_record.append({
            "long": deepcopy(self.long_term_memory),
            "short": deepcopy(self.short_term_meomry)
        })
        return self.history_record[-1]

    def history(self):
        return self.history_record

    def _get_metadata(self, data):
        return {
            "data": data,
            "hash": hashlib.md5(data.encode()).hexdigest(),
            "created_at": datetime.now(pytz.timezone("US/Pacific")).isoformat(),
            "action": "UPDATE"
        }

    def _pack_short_mem(self, data) -> dict | None:
        return self._get_metadata(data)

    def _pack_long_mem(self, data) -> dict | None:
        # because updating the mem requires accessing the LLM,
        # so we only update the mem in slow mode to avoid unnecessary overhead.
        if prompt_manager.get_mode(self.service_name) != "slow":
            return self._get_metadata("")

        long_mem = self.long_term_memory['data'] if self.long_term_memory else ""
        allowed_set = {
            "application": self.service_name
        }
        mem0_prompt = prompt_manager.format_prompt(self.service_name, "slow", "mem", allowed_set)
        parsed_message = mem0_prompt + "\n" + \
            long_mem + "\n" + \
            data + "\n" + \
            "Create memory summary of the above conversation."

        memory_content = get_llm_response(prompt=parsed_message)

        return self._get_metadata(memory_content)
