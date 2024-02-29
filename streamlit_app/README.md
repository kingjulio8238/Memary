# Streamlit App Demo

## Usage
- create `.env` file for `OPENAI_KEY`, `NEO4J_PW`, and `NEO4J_URL`
- install libraries using `pip install -r requirements.txt`
- run using `streamlit run app.py`

## Description
NOTE: For demo, database must not be empty (at least 1 chapter) to begin
### Knowledge Graph
- With a database only injected with chapter 1, graph starts with chapter 1 nodes
- Slider determines which chapter to inject into knowledge graph
- Displayed knowledge graph shows progression
### Recursive Retrieval
- Knowledge graph is initially entire knowledge store
- Type natural language query in &rarr; 
  - answer in natural lanugage
  - neo4j cypher for subgraph (using `UNION` to support multiple subgraphs for now)
  - subgraph that answer searched on