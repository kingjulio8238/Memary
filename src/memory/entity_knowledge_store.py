from datetime import datetime
from collections import defaultdict

from src.memory import (
    BaseMemory, MemoryStream, EntityMemoryItem)

class EntityKnowledgeStore(BaseMemory):
    def __init__(self, file_name=None):
        self.entity_memory = []
        super().__init__(file_name)

    def init_memory(self):
        self.load_memory_from_file()

        memory = defaultdict(lambda: {"count": 0, "date": None})
        # Process each item in the provided data
        for item in self.memory:
            entity = item["entity"]
            date = datetime.fromisoformat(item["date"])

            # Update count
            memory[entity]["count"] += 1

            # Update the most recent date if necessary
            if memory[entity]["date"] is None or date > memory[entity]["date"]:
                memory[entity]["date"] = date

        # Convert summary_data to the desired output format
        self.entity_memory = [
            {
                "entity": key,
                "count": value["count"],
                "date": value["date"].isoformat()
            } for key, value in memory.items()]

        # Print the summary list
        for entity_memory in self.entity_memory:
            print(entity_memory)

    def add_memory(self, memory_stream):
        self.memory.extend(memory_stream)

    def get_memory(self):
        return self.memory
