from src.modules.routing_agent import RoutingAgent
from src.memory.memory_stream import MemoryStream
from src.memory.entity_knowledge_store import EntityKnowledgeStore
from src.agent.data_types import Message

from src.agent.llm_api.tools import openai_chat_completions_request


class Agent():
    """Agent manages the reAct agent and the memory module."""

    def __init__(self, name, memory_stream_json, entity_knowledge_store_json,
                 system_persona_txt, user_persona_txt, past_chat_json) -> None:
        self.name = name
        self.routing_agent = RoutingAgent()
        self.memory_stream = MemoryStream(memory_stream_json)
        self.entity_knowledge_store = EntityKnowledgeStore(entity_knowledge_store_json)
        self.message = Message(system_persona_txt, user_persona_txt, past_chat_json)

    def __str__(self):
        return f"Agent {self.name}"
    
    def _change_llm_message_chatgpt(self) -> dict:
        """Change the llm_message to chatgpt format.

        Returns:
            dict: llm_message in chatgpt format
        """
        llm_message_chatgpt = self.message.llm_message
        llm_message_chatgpt['messages'] = [
            context.to_dict()
            for context in self.message.llm_message['messages']
        ]
        llm_message_chatgpt['messages'].append({
            'role':
            'user',
            'content':
            'Memory Stream:' + str([
                memory.to_dict()
                for memory in self.message.llm_message.pop('memory_stream')
            ])
        })
        llm_message_chatgpt['messages'].append({
            'role':
            'user',
            'content':
            'Knowledge Entity Store:' + str([
                entity.to_dict() for entity in self.message.llm_message.pop(
                    'knowledge_entity_store')
            ])
        })
        return llm_message_chatgpt
    
    def get_response(self) -> str:
        """Get response from the RAG model.

        Returns:
            str: response from the RAG model
        """
        llm_message_chatgpt = self._change_llm_message_chatgpt()
        response = openai_chat_completions_request(self.model_endpoint,
                                                   self.openai_api_key,
                                                   llm_message_chatgpt)
        response = str(response['choices'][0]['message']['content'])
        return response