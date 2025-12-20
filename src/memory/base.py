from abc import ABC, abstractmethod

class MemoryBase(ABC):
    @abstractmethod
    def get(self, memory_id:int):
        """
        Get the latest long-term and short-term memory.

        Args:
            memory_id (str): ID of the memory to update. If -1, return the latest meomory.

        Returns:
            dict: Retrieved memory.
        """
        pass

    @abstractmethod
    def update(self, data:str):
        """
        Update a memory.

        Args:
            data (str): New content to update the memory with.

        Returns:
            dict: Success message indicating the memory was updated.
        """
        pass

    @abstractmethod
    def history(self):
        """
        Get the history of changes for a memory by ID.

        Args:
            None

        Returns:
            list: List of changes for the memory.
        """
        pass


