import json
import logging
from datetime import datetime, timedelta

from src.memory.types import MemoryItem

logging.basicConfig(level=logging.INFO)

class MemoryStream:
    def __init__(self, file_name=None, data=None):
        self.file_name = file_name
        self.memory = []
        if file_name:
            self.load_memory_from_file()
        if data:
            self.add_memory(data)

    def __len__(self):
        return len(self.memory)

    def load_memory_from_file(self):
        try:
            with open(self.file_name, 'r') as file:
                self.memory = [MemoryItem.from_dict(item) for item in json.load(file)]
            logging.info(f"Memory loaded from {self.file_name} successfully.")
        except FileNotFoundError:
            logging.info("File not found. Starting with an empty memory.")

    def add_memory(self, data):
        self.memory.extend(data)
        logging.info("Memory added successfully.")

    def get_memory(self):
        return self.memory

    def remove_old_memory(self, days):
        cutoff_date = datetime.now() - timedelta(days=days)
        self.memory = [item for item in self.memory if item.date >= cutoff_date]
        logging.info("Old memory removed successfully.")

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
