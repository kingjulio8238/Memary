import tiktoken
from typing import Optional, List

from src.agent.base_agent import Agent
from src.agent.data_types import Context


class ChatAgent(Agent):

    def __init__(self, name, memory_stream_json, entity_knowledge_store_json,
                 system_persona_txt, user_persona_txt, past_chat_json):
        super().__init__(name, memory_stream_json, entity_knowledge_store_json,
                         system_persona_txt, user_persona_txt, past_chat_json)

    def add_chat(self,
                 role: str,
                 content: str,
                 entities: Optional[List[str]] = None):
        """Add a chat to the agent's memory.

        Args:
            role (str): 'system' or 'user'
            content (str): content of the chat
            entities (Optional[List[str]], optional): entities from Memory systems. Defaults to None.
        """
        # Add a chat to the agent's memory.
        self._add_contexts_to_llm_message(role, content)

        if entities:
            self.memory_stream.add_memory(entities)
            self.memory_stream.save_memory()
            self.entity_knowledge_store.add_memory(
                self.memory_stream.get_memory())
            self.entity_knowledge_store.save_memory()

        self._replace_memory_from_llm_message()
        self._replace_eks_to_from_message()

    def get_chat(self):
        return self.contexts

    def _add_contexts_to_llm_message(self, role, content, index=None):
        """Add contexts to the llm_message."""
        if index:
            self.message.llm_message["messages"].insert(index, Context(
                role, content))
        else:
            self.message.llm_message["messages"].append(Context(role, content))

    def _replace_memory_from_llm_message(self):
        """Replace the memory_stream from the llm_message."""
        self.message.llm_message[
            "memory_stream"] = self.memory_stream.get_memory()

    def _replace_eks_to_from_message(self):
        """Replace the entity knowledge store from the llm_message.
        eks = entity knowledge store"""

        self.message.llm_message[
            "knowledge_entity_store"] = self.entity_knowledge_store.get_memory(
            )
