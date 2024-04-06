import os
import sys
import random
import textwrap

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import pandas as pd

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
from neo4j import GraphDatabase
from pyvis.network import Network
from synonym_expand.synonym import custom_synonym_expand_fn

sys.path.append("..")
from src.memory import MemoryStream, EntityKnowledgeStore

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_KEY")


username = "neo4j"
password = os.getenv("NEO4J_PW")
url = os.getenv("NEO4J_URL")
database = "neo4j"
memory_stream_json = "memory_stream.json"
entity_knowledge_store_json = "entity_knowledge_store.json"
pplx_api_key = os.getenv('PERPLEXITY_API_KEY')

llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
query_llm = Perplexity(
    api_key=pplx_api_key, model="mistral-7b-instruct", temperature=0.5
)
Settings.llm = llm
Settings.chunk_size = 512

graph_store = Neo4jGraphStore(
    username=username,
    password=password,
    url=url,
    database=database,
)

memory_stream = MemoryStream(memory_stream_json)
entity_knowledge_store = EntityKnowledgeStore(entity_knowledge_store_json)

def add_memory_item(entities):
    memory_stream.add_memory(entities)
    print("memory_stream: ", memory_stream.get_memory())

def check_KG(query):
    storage_context = StorageContext.from_defaults(graph_store=graph_store)

    graph_rag_retriever = KnowledgeGraphRAGRetriever(
        storage_context=storage_context,
        verbose=True,
        llm=llm,
        retriever_mode="keyword",
        with_nl2graphquery=True,
        synonym_expand_fn=custom_synonym_expand_fn,
    )

    query_engine = RetrieverQueryEngine.from_args(
        graph_rag_retriever,
    )
    response = query_engine.query(
        query,
    )

    if response.metadata is None:
        return False
    return True

def external_query(query):
    # 1) must query the web
    messages_dict = [
        {"role": "system", "content": "Be precise and concise."},
        {"role": "user", "content": query},
    ]
    messages = [ChatMessage(**msg) for msg in messages_dict]

    external_response = query_llm.chat(messages)

    # 2) answer needs to be stored into txt file for loading into KG
    with open('data/external_response.txt', 'w') as f:
        print(external_response, file=f)
    return str(external_response)

def load_KG():
    storage_context = StorageContext.from_defaults(graph_store=graph_store)
    documents = SimpleDirectoryReader(
        input_files=['data/external_response.txt']
    ).load_data()

    index = KnowledgeGraphIndex.from_documents(
        documents,
        storage_context=storage_context,
        max_triplets_per_chunk=5,
    )

def get_response(query, return_entity=False):
    storage_context = StorageContext.from_defaults(graph_store=graph_store)

    graph_rag_retriever = KnowledgeGraphRAGRetriever(
        storage_context=storage_context,
        verbose=True,
        llm=llm,
        retriever_mode="keyword",
        with_nl2graphquery=True,
        synonym_expand_fn=custom_synonym_expand_fn,
    )

    query_engine = RetrieverQueryEngine.from_args(
        graph_rag_retriever,
    )
    response = query_engine.query(
        query,
    )

    if return_entity:
        return response, get_entity(query_engine.retrieve(query))
    return response

def get_entity(retrieve) -> list[str]:
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
    ENTITY_EXCEPTIONS = ['Unknown relation']

    entities = []
    kg_rel_map = retrieve[0].node.metadata["kg_rel_map"]
    for key, items in kg_rel_map.items():
        # key is the entity of question
        entities.append(key)
        # items is a list of [relationship, entity]
        entities.extend(item[1] for item in items)
    entities = list(set(entities))
    for exceptions in ENTITY_EXCEPTIONS:
        if exceptions in entities:
            entities.remove(exceptions)
    return entities

def create_graph(nodes, edges):
    g = Network(
        notebook=True,
        directed=True,
        cdn_resources="in_line",
        height="500px",
        width="100%",
    )

    for node in nodes:
        g.add_node(node, label=node, title=node)
    for edge in edges:
        # assuming only one relationship type per edge
        g.add_edge(edge[0], edge[1], label=edge[2][0])

    g.repulsion(
        node_distance=200,
        central_gravity=0.12,
        spring_length=150,
        spring_strength=0.05,
        damping=0.09,
    )
    return g


def generate_string(entities):
    cypher_query = 'MATCH p = (n) - [*1 .. 2] - ()\n'
    cypher_query += 'WHERE n.id IN ' + str(entities) + '\n'
    cypher_query += 'RETURN p'

    return cypher_query


def add_chapter(paths):
    documents = SimpleDirectoryReader(
        input_files=paths  # paths is list of chapters
    ).load_data()
    storage_context = StorageContext.from_defaults(graph_store=graph_store)

    index = KnowledgeGraphIndex.from_documents(
        documents,
        storage_context=storage_context,
        max_triplets_per_chunk=2,
    )


def fill_graph(nodes, edges, cypher_query):
    entities = []
    with GraphDatabase.driver(
        uri=os.getenv("NEO4J_URL"), auth=("neo4j", os.getenv("NEO4J_PW"))
    ) as driver:
        with driver.session() as session:
            result = session.run(cypher_query)
            for record in result:
                path = record["p"]
                rels = [rel.type for rel in path.relationships]

                n1_id = record["p"].nodes[0]["id"]
                n2_id = record["p"].nodes[1]["id"]
                nodes.add(n1_id)
                nodes.add(n2_id)
                edges.append((n1_id, n2_id, rels))
                entities.extend([n1_id, n2_id])


tab1, tab2 = st.tabs(["Knowledge Graph", "Recursive Retrieval"])

with tab1:
    cypher_query = """
        MATCH p = (:Entity)-[r]-()  RETURN p, r LIMIT 1000;
    """
    st.title("Knowledge Graph")

    nodes = set()
    edges = []

    val = st.slider(
        "Select a chapter to add", min_value=2, max_value=5, value=2, step=1
    )
    add_clicked = st.button("Inject into Graph")
    st.text("")

    if add_clicked:
        paths = [f"data/harry_potter/{val}.txt"]
        add_chapter(paths)

    fill_graph(nodes, edges, cypher_query)
    graph = create_graph(nodes, edges)
    graph_html = graph.generate_html(f"graph_{random.randint(0, 1000)}.html")
    components.html(graph_html, height=500, scrolling=True)


with tab2:
    cypher_query = "MATCH p = (:Entity)-[r]-()  RETURN p, r LIMIT 1000;"
    answer = ""
    external_response = ""
    st.title("Recursive Retrieval")
    query = st.text_input("Ask a question")
    generate_clicked = st.button("Generate")

    st.write("")

    if generate_clicked:
        external_response = ""
        if check_KG(query):
            response, entities = get_response(query, return_entity=True)
            add_memory_item(entities)
            cypher_query = generate_string(
                list(list(response.metadata.values())[0]["kg_rel_map"].keys())
            )
            answer = str(response)
        else:
            # get response
            external_response = "No response found in knowledge graph, querying web instead with "
            external_response += external_query(query)
            display_external = textwrap.fill(external_response, width=80)
            st.text(display_external)
            # load into KG
            load_KG()

    nodes = set()
    edges = []  # (node1, node2, [relationships])
    fill_graph(nodes, edges, cypher_query)

    wrapped_text = textwrap.fill(answer, width=80)
    st.text(wrapped_text)
    st.code("# Current Cypher Used\n" + cypher_query)
    st.write("")
    st.markdown("Current Subgraph Used")
    graph = create_graph(nodes, edges)
    graph_html = graph.generate_html(f"graph_{random.randint(0, 1000)}.html")
    components.html(graph_html, height=500, scrolling=True)

    if len(memory_stream) > 0:
        memory_items = memory_stream.get_memory()
        # Convert to DataFrame
        memory_items_dicts = [item.to_dict() for item in memory_items]
        df = pd.DataFrame(memory_items_dicts)
        st.write("Memory Stream")
        st.dataframe(df)
        memory_stream.save_memory()

        st.text("Entity Knowledge Store")
        entity_knowledge_store.add_memory(memory_stream.get_memory())
        entity_knowledge_store.save_memory()

        # Convert to DataFrame
        knowledge_memory_items = entity_knowledge_store.get_memory()
        knowledge_memory_items_dicts = [item.to_dict() for item in knowledge_memory_items]
        df_knowledge = pd.DataFrame(knowledge_memory_items_dicts)
        st.dataframe(df_knowledge)
