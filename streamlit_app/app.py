import os
import random
import textwrap

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from llama_index.core import (
    KnowledgeGraphIndex,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.openai import OpenAI
from neo4j import GraphDatabase
from pyvis.network import Network

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_KEY")


username = "neo4j"
password = os.getenv("NEO4J_PW")
url = os.getenv("NEO4J_URL")
database = "neo4j"

llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.llm = llm
Settings.chunk_size = 512

graph_store = Neo4jGraphStore(
    username=username,
    password=password,
    url=url,
    database=database,
)


def get_response(query):
    storage_context = StorageContext.from_defaults(graph_store=graph_store)

    graph_rag_retriever = KnowledgeGraphRAGRetriever(
        storage_context=storage_context,
        verbose=True,
    )
    query_engine = RetrieverQueryEngine.from_args(
        graph_rag_retriever,
    )
    response = query_engine.query(
        query,
    )
    return response


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
    cypher_query = 'MATCH p = (:Entity { id: "' + entities[0] + '"})-[*1]->()\n'
    cypher_query += "RETURN p"

    for e in entities[1:]:
        cypher_query += "\n"
        cypher_query += "UNION\n"
        cypher_query += 'MATCH p = (:Entity { id: "' + e + '"})-[*1]->()\n'
        cypher_query += "RETURN p"
    cypher_query += ";"
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
    st.title("Recursive Retrieval")
    query = st.text_input("Ask a question")
    generate_clicked = st.button("Generate")
    st.write("")

    if generate_clicked:
        response = get_response(query)
        cypher_query = generate_string(
            list(list(response.metadata.values())[0]["kg_rel_map"].keys())
        )
        answer = str(response)

    nodes = set()
    edges = []  # (node1, node2, [relationships])
    fill_graph(nodes, edges, cypher_query)

    wrapped_text = textwrap.fill(answer, width=60)
    st.text(wrapped_text)
    st.code("# Current Cypher Used\n" + cypher_query)
    st.write("")
    st.markdown("Current Subgraph Used")
    graph = create_graph(nodes, edges)
    graph_html = graph.generate_html(f"graph_{random.randint(0, 1000)}.html")
    components.html(graph_html, height=500, scrolling=True)
