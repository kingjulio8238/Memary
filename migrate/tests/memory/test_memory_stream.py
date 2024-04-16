import unittest
import os
from datetime import datetime, timedelta
from src.memory import MemoryStream
from src.memory.types import MemoryItem

class TestMemoryStream(unittest.TestCase):
    def setUp(self):
        self.file_name = "tests/memory/test_memory.json"
        self.memory_stream = MemoryStream(file_name=self.file_name)

    def tearDown(self):
        # Clean up test file after each test
        try:
            os.remove(self.file_name)
        except FileNotFoundError:
            pass

    def test_add_memory(self):
        data = [MemoryItem("test_entity", datetime.now().replace(microsecond=0))]
        self.memory_stream.add_memory(data)
        self.assertEqual(len(self.memory_stream), 1)
        self.assertEqual(self.memory_stream.get_memory()[0], data[0])

    def test_remove_old_memory(self):
        past_date = datetime.now().replace(microsecond=0) - timedelta(days=10)
        self.memory_stream.add_memory([MemoryItem("old_entity", past_date)])
        self.memory_stream.remove_old_memory(5)
        self.assertEqual(len(self.memory_stream.get_memory()), 0)

    def test_save_and_load_memory(self):
        data = [MemoryItem("test_entity", datetime.now().replace(microsecond=0))]
        self.memory_stream.add_memory(data)
        self.memory_stream.save_memory()
        new_memory_stream = MemoryStream(file_name=self.file_name)
        self.assertEqual(len(new_memory_stream), len(self.memory_stream))
        self.assertEqual(new_memory_stream.get_memory(), self.memory_stream.get_memory())

    def test_get_memory_by_index(self):
        data = [MemoryItem("entity1", datetime.now().replace(microsecond=0)), MemoryItem("entity2", datetime.now().replace(microsecond=0))]
        self.memory_stream.add_memory(data)
        self.assertEqual(self.memory_stream.get_memory_by_index(1), data[1])

    def test_remove_memory_by_index(self):
        data = [MemoryItem("entity1", datetime.now().replace(microsecond=0)), MemoryItem("entity2", datetime.now().replace(microsecond=0))]
        self.memory_stream.add_memory(data)
        self.memory_stream.remove_memory_by_index(0)
        self.assertEqual(len(self.memory_stream), 1)
        self.assertEqual(self.memory_stream.get_memory()[0], data[1])

if __name__ == '__main__':
    unittest.main()
