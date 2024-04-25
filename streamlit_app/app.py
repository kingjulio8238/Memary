import sys
import random
import textwrap
import os

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import pandas as pd
from pyvis.network import Network
from neo4j import GraphDatabase

# src should sit in the same level as /streamlit_app
curr_dir = os.getcwd()
parent_dir = os.path.dirname(curr_dir)
print(parent_dir)
sys.path.append(parent_dir)

from src.agent.chat_agent import ChatAgent

load_dotenv()

system_persona_txt = "data/system_persona.txt"
user_persona_txt = "data/user_persona.txt"
past_chat_json = "data/past_chat.json"
memory_stream_json = "data/memory_stream.json"
entity_knowledge_store_json = "data/entity_knowledge_store.json"
chat_agent = ChatAgent("Personal Agent",
                  memory_stream_json,
                  entity_knowledge_store_json,
                  system_persona_txt,
                  user_persona_txt,
                  past_chat_json)

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


def fill_graph(nodes, edges, cypher_query):
    entities = []
    with GraphDatabase.driver(
        uri=chat_agent.neo4j_url, auth=(chat_agent.neo4j_username, chat_agent.neo4j_password)
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
        chat_agent.add_chapter(paths)

    fill_graph(nodes, edges, cypher_query)
    graph = create_graph(nodes, edges)
    graph_html = graph.generate_html(f"graph_{random.randint(0, 1000)}.html")
    components.html(graph_html, height=500, scrolling=True)


with tab2:
    cypher_query = "MATCH p = (:Entity)-[r]-()  RETURN p, r LIMIT 1000;"
    answer = ""
    external_response = ""
    st.title("meMary Chatbot")
    query = st.text_input("Ask a question")
    generate_clicked = st.button("Generate")

    st.write("")

    if generate_clicked:
        external_response = ""
        rag_response = "There was no information in knowledge_graph to answer your question."
        chat_agent.add_chat('user', query)
        cypher_query = chat_agent.check_KG(query)
        if cypher_query:
            rag_response, entities = chat_agent.get_routing_agent_response(query, return_entity=True)
            chat_agent.add_chat('user', 'rag: ' + rag_response, entities)
        else:
            # get response
            external_response = "No response found in knowledge graph, querying web instead with "
            query_answer = chat_agent.get_routing_agent_response(query)
            external_response += query_answer
            chat_agent.add_chat('user', 'external response: ' + query_answer)
            display_external = textwrap.fill(external_response, width=80)
            st.text(display_external)

        answer = chat_agent.get_response()
        st.title("RAG Response")
        st.text(str(rag_response))
        if cypher_query:
            nodes = set()
            edges = []  # (node1, node2, [relationships])
            fill_graph(nodes, edges, cypher_query)

            st.code("# Current Cypher Used\n" + cypher_query)
            st.write("")
            st.markdown("Current Subgraph Used")
            graph = create_graph(nodes, edges)
            graph_html = graph.generate_html(f"graph_{random.randint(0, 1000)}.html")
            components.html(graph_html, height=500, scrolling=True)
        else:
            st.text("No information found in the knowledge graph")
        st.title("Perplexity Response")
        wrapped_text = textwrap.fill(str(external_response), width=80)
        st.text(wrapped_text)

        st.title("Final Response")
        wrapped_text = textwrap.fill(answer, width=80)
        st.text(wrapped_text)

        if len(chat_agent.memory_stream) > 0:
            # Memory Stream
            memory_items = chat_agent.memory_stream.get_memory()
            memory_items_dicts = [item.to_dict() for item in memory_items]
            df = pd.DataFrame(memory_items_dicts)
            st.write("Memory Stream")
            st.dataframe(df)

            # Entity Knowledge Store
            knowledge_memory_items = chat_agent.entity_knowledge_store.get_memory()
            knowledge_memory_items_dicts = [item.to_dict() for item in knowledge_memory_items]
            df_knowledge = pd.DataFrame(knowledge_memory_items_dicts)
            st.text("Entity Knowledge Store")
            st.dataframe(df_knowledge)
