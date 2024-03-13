import unittest
import os
from datetime import datetime
from src.memory import EntityKnowledgeStore
from src.memory.types import KnowledgeMemoryItem, MemoryItem


class TestEntityKnowledgeStore(unittest.TestCase):

    def setUp(self):
        self.file_name = "tests/memory/test_knowledge_memory.json"
        self.entity_knowledge_store = EntityKnowledgeStore(
            file_name=self.file_name)

    def tearDown(self):
        # Clean up test file after each test
        try:
            os.remove(self.file_name)
        except FileNotFoundError:
            pass

    def test_add_memory(self):
        data = [
            MemoryItem("test_entity",
                       datetime.now().replace(microsecond=0))
        ]
        self.entity_knowledge_store.add_memory(data)
        assert len(self.entity_knowledge_store.knowledge_memory) == 1
        assert isinstance(self.entity_knowledge_store.knowledge_memory[0],
                          KnowledgeMemoryItem)

    def test_convert_memory_to_knowledge_memory(self):
        data = [
            MemoryItem("test_entity",
                       datetime.now().replace(microsecond=0))
        ]
        converted_data = self.entity_knowledge_store._convert_memory_to_knowledge_memory(
            data)
        assert len(converted_data) == 1
        assert isinstance(converted_data[0], KnowledgeMemoryItem)

    def test_update_knowledge_memory(self):
        data = [
            KnowledgeMemoryItem("knowledge_entity", 1,
                                datetime.now().replace(microsecond=0))
        ]
        self.entity_knowledge_store._update_knowledge_memory(data)
        assert len(self.entity_knowledge_store.knowledge_memory) == 1
        assert self.entity_knowledge_store.knowledge_memory[0] == data[0]
