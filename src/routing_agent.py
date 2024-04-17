import os

import geocoder
import googlemaps
from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext
from llama_index.core.agent import ReActAgent
from llama_index.core.llms import ChatMessage
from llama_index.core.multi_modal_llms.generic_utils import load_image_urls
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever
from llama_index.core.tools import FunctionTool
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.openai import OpenAI
from llama_index.llms.perplexity import Perplexity
from llama_index.multi_modal_llms.openai import OpenAIMultiModal

from synonym_expand.synonym import custom_synonym_expand_fn


class RoutingAgent:
    def __init__(self) -> None:
        load_dotenv()
        # getting necessary API keys
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_KEY")
        googlemaps_api_key = os.getenv("GOOGLEMAPS_API_KEY")
        pplx_api_key = os.getenv("PERPLEXITY_API_KEY")

        # Neo4j credentials
        self.neo4j_username = "neo4j"
        self.neo4j_password = os.getenv("NEO4J_PW")
        self.neo4j_url = os.getenv("NEO4J_URL")
        database = "neo4j"

        # initialize APIs
        self.openai_mm_llm = OpenAIMultiModal(
            model="gpt-4-vision-preview",
            api_key=os.getenv("OPENAI_KEY"),
            max_new_tokens=300,
        )
        llm = OpenAI(model="gpt-3.5-turbo-instruct")
        self.query_llm = Perplexity(
            api_key=pplx_api_key, model="mistral-7b-instruct", temperature=0.5
        )
        self.gmaps = googlemaps.Client(key=googlemaps_api_key)
        Settings.llm = llm
        Settings.chunk_size = 512

        # initialize Neo4j graph resources
        graph_store = Neo4jGraphStore(
            username=self.neo4j_username,
            password=self.neo4j_password,
            url=self.neo4j_url,
            database=database,
        )

        graph_rag_retriever = KnowledgeGraphRAGRetriever(
            storage_context=StorageContext.from_defaults(graph_store=graph_store),
            verbose=True,
            llm=llm,
            retriever_mode="keyword",
            with_nl2graphquery=True,
            synonym_expand_fn=custom_synonym_expand_fn,
        )

        self.query_engine = RetrieverQueryEngine.from_args(
            graph_rag_retriever,
        )

        search_tool = FunctionTool.from_defaults(fn=self.search)
        locate_tool = FunctionTool.from_defaults(fn=self.locate)
        vision_tool = FunctionTool.from_defaults(fn=self.vision)

        self.agent = ReActAgent.from_tools(
            [search_tool, locate_tool, vision_tool], llm=llm, verbose=True
        )

    def external_query(self, query: str):
        messages_dict = [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": query},
        ]
        messages = [ChatMessage(**msg) for msg in messages_dict]
        external_response = self.query_llm.chat(messages)

        return str(external_response)

    def search(self, query: str) -> str:
        """Search the knowledge graph or perform search on the web if information is not present in the knowledge graph"""
        response = self.query_engine.query(query)

        if response.metadata is None:
            return self.external_query(query)
        else:
            return response

    def locate(self, query: str) -> str:
        """Finds the current geographical location"""
        location = geocoder.ip("me")
        lattitude, longitude = location.latlng[0], location.latlng[1]

        reverse_geocode_result = self.gmaps.reverse_geocode((lattitude, longitude))
        formatted_address = reverse_geocode_result[0]["formatted_address"]
        return "Your address is" + formatted_address

    def vision(self, query: str, img_url: str) -> str:
        """Uses computer vision to process the image specified by the image url and answers the question based on the CV results"""
        img_docs = load_image_urls([img_url])
        response = self.openai_mm_llm.complete(prompt=query, image_documents=img_docs)
        return response

    def query(self, query: str) -> str:
        # get the response from react agent
        response = self.agent.chat(query)
        # write response to file for KG writeback
        with open('data/external_response.txt', 'w') as f:
            print(response, file=f)


# testing
# r = RoutingAgent()
# r.query("who is harry potter")