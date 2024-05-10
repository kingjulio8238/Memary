from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage


llm = Ollama(model="llama3", request_timeout=60.0)
messages_dict = [
    {"role": "system", "content": "Be precise and concise."},
    {"role": "user", "content": "Why is the sky blue?"},
]
messages = [ChatMessage(**msg) for msg in messages_dict]

print(llm.chat(
    messages=messages,
))