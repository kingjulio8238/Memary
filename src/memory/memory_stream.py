import json
import logging
from datetime import datetime, timedelta

from src.memory import BaseMemory, MemoryItem

logging.basicConfig(level=logging.INFO)

class MemoryStream(BaseMemory):

    def init_memory(self):
        """Initializes memory."""
        self.load_memory_from_file()
        if self.data:
            self.add_memory(self.data)

    def add_memory(self, data):
        self.memory.extend(data)

    def load_memory_from_file(self):
        try:
            with open(self.file_name, 'r') as file:
                self.memory = [MemoryItem.from_dict(item) for item in json.load(file)]
            logging.info(f"Memory loaded from {self.file_name} successfully.")
        except FileNotFoundError:
            logging.info("File not found. Starting with an empty memory.")

    def remove_old_memory(self, days):
        cutoff_date = datetime.now() - timedelta(days=days)
        self.memory = [item for item in self.memory if item.date >= cutoff_date]
        logging.info("Old memory removed successfully.")
