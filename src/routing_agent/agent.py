import os

import geocoder
import googlemaps
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool, StructuredTool, tool
from llama_index.core import (KnowledgeGraphIndex, Settings,
                              SimpleDirectoryReader, StorageContext)
from llama_index.core.llms import ChatMessage
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.openai import OpenAI as llamaOpenAI
from langchain_openai import OpenAI as langOpenAI
from llama_index.llms.perplexity import Perplexity
from synonym_expand.synonym import custom_synonym_expand_fn

from tools import SearchKG
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

class RoutingAgent:
    def __init__(self) -> None:
        load_dotenv()
        # API keys
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_KEY")
        self.pplx_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.googlemaps_api_key = os.getenv("GOOGLEMAPS_API_KEY")

        # Neo4j credentials
        self.neo4j_username = "neo4j"
        self.neo4j_password = os.getenv("NEO4J_PW")
        self.neo4j_url = os.getenv("NEO4J_URL")
        database = "neo4j"

        # setting up clients
        self.llm = llamaOpenAI(temperature=0, model="gpt-3.5-turbo")
        self.query_llm = Perplexity(
            api_key=self.pplx_api_key, model="mistral-7b-instruct", temperature=0.5
        )
        self.gmaps = googlemaps.Client(key=self.googlemaps_api_key)

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



        # setting up routing agent
        langchain_llm = langOpenAI(model="gpt-3.5-turbo-instruct")
        prompt = hub.pull("hwchase17/react")
        # tools = [self.searchKG, self.locationService]
        tools = [SearchKG()]
        agent = create_react_agent(langchain_llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    def external_query(self, query: str):
        messages_dict = [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": query},
        ]
        messages = [ChatMessage(**msg) for msg in messages_dict]
        external_response = self.query_llm.chat(messages)

        return str(external_response)
    

    @tool
    def searchKG(self, query: str) -> str:
        """Search the knowledge graph or perform search on the web if information is not present in the knowledge graph"""

        response = self.query_engine.query(query)

        if response.metadata is None:
            return self.external_query(query)
        else:
            return response

    @tool
    def locationService(self, query: str) -> str:
        """Use googlempas to get information about the current location"""
        location = geocoder.ip("me")
        lattitude, longitude = location.latlng[0], location.latlng[1]
        reverse_geocode_result = self.gmaps.reverse_geocode((lattitude, longitude))
        formatted_address = reverse_geocode_result[0]["formatted_address"]
        return "Your address is" + formatted_address
    

