import os
from llama_index.core import (
    KnowledgeGraphIndex,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.llms.perplexity import Perplexity

from src.synonym_expand.synonym import custom_synonym_expand_fn
from src.memory import MemoryStream, EntityKnowledgeStore
from src.agent.data_types import Message
from src.agent.llm_api.tools import openai_chat_completions_request

MAX_ENTITIES_FROM_KG = 5
ENTITY_EXCEPTIONS = ['Unknown relation']


class Agent(object):
    """Agent manages the RAG model, the knowledge graph, and the memory stream."""

    def __init__(self, name, memory_stream_json, entity_knowledge_store_json,
                 system_persona_txt, user_persona_txt, past_chat_json):
        self.name = name
        # OpenAI API key
        self.openai_api_key = os.environ["OPENAI_API_KEY"]
        self.model_endpoint = 'https://api.openai.com/v1'
        # Neo4j credentials
        self.neo4j_username = "neo4j"
        self.neo4j_password = os.getenv("NEO4J_PW")
        self.neo4j_url = os.getenv("NEO4J_URL")
        database = "neo4j"
        # Perplexity API key
        pplx_api_key = os.getenv('PERPLEXITY_API_KEY')

        self.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
        self.query_llm = Perplexity(api_key=pplx_api_key,
                                    model="sonar-small-online",
                                    temperature=0.5)
        Settings.llm = self.llm
        Settings.chunk_size = 512

        self.graph_store = Neo4jGraphStore(
            username=self.neo4j_username,
            password=self.neo4j_password,
            url=self.neo4j_url,
            database=database,
        )

        self.storage_context = StorageContext.from_defaults(
            graph_store=self.graph_store)

        self.graph_rag_retriever = KnowledgeGraphRAGRetriever(
            storage_context=self.storage_context,
            verbose=True,
            llm=self.llm,
            retriever_mode="keyword",
            with_nl2graphquery=True,
            synonym_expand_fn=custom_synonym_expand_fn,
        )
        self.query_engine = RetrieverQueryEngine.from_args(
            self.graph_rag_retriever, )

        self.memory_stream = MemoryStream(memory_stream_json)
        self.entity_knowledge_store = EntityKnowledgeStore(
            entity_knowledge_store_json)

        self.message = Message(system_persona_txt, user_persona_txt,
                               past_chat_json)

    def __str__(self):
        return f"Agent {self.name}"

    def check_KG(self, query: str) -> bool:
        """Check if the query is in the knowledge graph.

        Args:
            query (str): query to check in the knowledge graph

        Returns:
            bool: True if the query is in the knowledge graph, False otherwise
        """
        response = self.query_engine.query(query)

        if response.metadata is None:
            return False
        return True

    def external_query(self, query: str):
        # 1) must query the web
        messages_dict = [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": query
            },
        ]
        messages = [ChatMessage(**msg) for msg in messages_dict]

        external_response = self.query_llm.chat(messages)

        # 2) answer needs to be stored into txt file for loading into KG
        with open('data/external_response.txt', 'w') as f:
            print(external_response, file=f)
        return str(external_response)

    def load_KG(self):
        # TODO: index should be updated with the new data
        documents = SimpleDirectoryReader(
            input_files=['data/external_response.txt']).load_data()

        index = KnowledgeGraphIndex.from_documents(
            documents,
            storage_context=self.storage_context,
            max_triplets_per_chunk=5,
        )

    def add_chapter(self, paths):
        # TODO: index should be updated with the new data
        documents = SimpleDirectoryReader(
            input_files=paths  # paths is list of chapters
        ).load_data()

        index = KnowledgeGraphIndex.from_documents(
            documents,
            storage_context=self.storage_context,
            max_triplets_per_chunk=2,
        )

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

    def get_rag_response(self, query, return_entity=False):
        """Get response from the RAG model."""
        response = self.query_engine.query(query)

        if return_entity:
            return response, self.get_entity(self.query_engine.retrieve(query))
        return response

    def get_entity(self, retrieve) -> list[str]:
        """retrieve is a list of QueryBundle objects.
        A retrieved QueryBundle object has a "node" attribute,
        which has a "metadata" attribute.

        example for "kg_rel_map":
        kg_rel_map = {
            'Harry': [['DREAMED_OF', 'Unknown relation'], ['FELL_HARD_ON', 'Concrete floor']],
            'Potter': [['WORE', 'Round glasses'], ['HAD', 'Dream']]
        }

        Args:
            retrieve (list[NodeWithScore]): list of NodeWithScore objects
        return:
            list[str]: list of string entities
        """

        entities = []
        kg_rel_map = retrieve[0].node.metadata["kg_rel_map"]
        for key, items in kg_rel_map.items():
            # key is the entity of question
            entities.append(key)
            # items is a list of [relationship, entity]
            entities.extend(item[1] for item in items)
            if len(entities) > MAX_ENTITIES_FROM_KG:
                break
        entities = list(set(entities))
        for exceptions in ENTITY_EXCEPTIONS:
            if exceptions in entities:
                entities.remove(exceptions)
        return entities
