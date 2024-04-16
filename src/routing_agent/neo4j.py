from dotenv import load_dotenv
import os
from llama_index.llms.openai import OpenAI 
from llama_index.core import Settings, StorageContext
from llama_index.llms.perplexity import Perplexity
from llama_index.core.llms import ChatMessage
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from synonym_expand.synonym import custom_synonym_expand_fn


class Neo4JWrapper():
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def __init__(self) -> None:
        load_dotenv()

        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_KEY")
        self.pplx_api_key = os.getenv("PERPLEXITY_API_KEY")

        # Neo4j credentials
        self.neo4j_username = "neo4j"
        self.neo4j_password = os.getenv("NEO4J_PW")
        self.neo4j_url = os.getenv("NEO4J_URL")
        database = "neo4j"

        # setting up clients
        self.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
        self.query_llm = Perplexity(
            api_key=self.pplx_api_key, model="mistral-7b-instruct", temperature=0.5
        )

        Settings.llm = self.llm
        Settings.chunk_size = 512

        # KG search functionality
        graph_store = Neo4jGraphStore(
            username=self.neo4j_username,
            password=self.neo4j_password,
            url=self.neo4j_url,
            database=database,
        )

        graph_rag_retriever = KnowledgeGraphRAGRetriever(
            storage_context=StorageContext.from_defaults(graph_store=graph_store),
            verbose=True,
            llm=self.llm,
            retriever_mode="keyword",
            with_nl2graphquery=True,
            synonym_expand_fn=custom_synonym_expand_fn,
        )

        self.query_engine = RetrieverQueryEngine.from_args(
            graph_rag_retriever,
        )
    
    def external_query(self, query: str) -> str:
        messages_dict = [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": query},
        ]
        messages = [ChatMessage(**msg) for msg in messages_dict]
        external_response = self.query_llm.chat(messages)

        return str(external_response)
    
    def search_KG(self, query: str) -> str:
        response = self.query_engine.query(query)

        if response.metadata is None:
            return self.external_query(query)
        else:
            return response

