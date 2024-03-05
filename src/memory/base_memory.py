import json
import logging

from src.memory import MemoryItem

from abc import ABC, abstractmethod

class BaseMemory(ABC):
    def __init__(self, file_name: str, data=None):
        """Initializes the memory storage."""
        self.file_name = file_name
        self.data = data
        self.memory = []
        self.init_memory()

    def __len__(self):
        """Returns the number of items in the memory."""
        return len(self.memory)

    @abstractmethod
    def init_memory(self):
        """Initializes memory."""
        pass

    def load_memory_from_file(self):
        """Loads memory items from a file."""
        try:
            with open(self.file_name, 'r') as file:
                self.memory = [MemoryItem.from_dict(item) for item in json.load(file)]
            logging.info(f"Memory loaded from {self.file_name} successfully.")
        except FileNotFoundError:
            logging.info("File not found. Starting with an empty memory.")


    @abstractmethod
    def add_memory(self, data):
        """Adds new memory data."""
        pass

    def get_memory(self):
        return self.memory

    @abstractmethod
    def remove_old_memory(self, days):
        """Removes memory items older than a specified number of days."""
        pass

    def save_memory(self):
        if self.file_name:
            with open(self.file_name, 'w') as file:
                json.dump([item.to_dict() for item in self.memory], file, default=str, indent=4)
                logging.info(f"Memory saved to {self.file_name} successfully.")
        else:
            logging.info("No file name provided. Memory not saved.")

    def get_memory_by_index(self, index):
        if 0 <= index < len(self.memory):
            return self.memory[index]
        else:
            return None

    def remove_memory_by_index(self, index):
        if 0 <= index < len(self.memory):
            del self.memory[index]
            logging.info("Memory item removed successfully.")
            return True
        else:
            logging.info("Invalid index. Memory item not removed.")
            return False
