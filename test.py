from llama_index.multi_modal_llms.ollama import OllamaMultiModal
from pathlib import Path
import requests
import os
from llama_index.core import SimpleDirectoryReader
from llama_index.core.multi_modal_llms.generic_utils import load_image_urls

mm_modal = OllamaMultiModal(model="llava")
input_image_path = Path("test_images")
if not input_image_path.exists():
    Path.mkdir(input_image_path)

url = "https://t3.ftcdn.net/jpg/00/84/09/18/360_F_84091840_8wn1lAJ7jIuYRczt4PRqrrZUoAOoPVrO.jpg"
data = requests.get(url).content

with open('test_images/cow.jpg', 'wb') as f:
    f.write(data)
image_documents = SimpleDirectoryReader('test_images').load_data()

response = mm_modal.complete("what is in the image?", image_documents=image_documents)
print(response)
