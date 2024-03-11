import json
import logging
from datetime import datetime
from collections import defaultdict

from src.memory import (
    BaseMemory, MemoryStream, EntityMemoryItem)

class EntityKnowledgeStore(BaseMemory):

    def __len__(self):
        """Returns the number of items in the memory."""
        return len(self.knowledge_memory)

    def init_memory(self):
        """Initializes memory.
        self.entity_memory: list[EntityMemoryItem]
        """
        self.load_memory_from_file()
        if self.entity:
            self.add_memory(self.entity)

    @property
    def memory_to_save(self):
        return self.knowledge_memory

    def load_memory_from_file(self):
        try:
            with open(self.file_name, 'r') as file:
                self.memory = [
                    EntityMemoryItem.from_dict(item)
                    for item in json.load(file)
                ]
            logging.info(
                f"Entity Memory loaded from {self.file_name} successfully.")
        except FileNotFoundError:
            logging.info(
                "File not found. Starting with an empty entity memory.")

    def add_memory(self, memory_stream: list):
        self.knowledge_memory.extend(memory_stream)

    def convert_memory_to_entity_memory(self, memory_stream: list) -> list:
        entity_memory = defaultdict(int)
        for item in memory_stream:
            entity_memory[item.entity] += 1
        return [
            EntityMemoryItem(entity=entity, count=count, date=datetime.now())
            for entity, count in entity_memory.items()
        ]

    def get_memory(self) -> list:
        return self.knowledge_memory
