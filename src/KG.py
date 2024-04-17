import os

from dotenv import load_dotenv
from llama_index.core import (
    KnowledgeGraphIndex,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.openai import OpenAI


class KG:
    def __init__(self) -> None:
        load_dotenv()
        # getting necessary API keys
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_KEY")

        # Neo4j credentials
        self.neo4j_username = "neo4j"
        self.neo4j_password = os.getenv("NEO4J_PW")
        self.neo4j_url = os.getenv("NEO4J_URL")
        database = "neo4j"

        llm = OpenAI(model="gpt-3.5-turbo-instruct")
        Settings.llm = llm
        Settings.chunk_size = 512

        graph_store = Neo4jGraphStore(
            username=self.neo4j_username,
            password=self.neo4j_password,
            url=self.neo4j_url,
            database=database,
        )

        self.storage_context = StorageContext.from_defaults(graph_store=graph_store)

    def write_to_KG(self):
        documents = SimpleDirectoryReader(
            input_files=["data/external_response.txt"]
        ).load_data()

        index = KnowledgeGraphIndex.from_documents(
            documents,
            storage_context=self.storage_context,
            max_triplets_per_chunk=8,
        )
