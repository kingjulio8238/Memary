# Current Implementation of Recursive Retrieval
## Graph Rag + NL2GraphQuery
- Graph RAG extracts subgraph related to key entities in question
- NL2GraphQuery generates graph cypher based on query and schema
  - Note: Cypher not showing up in metadata right now
- Combination of these two contexts &rarr; LLM generates answer with all of this invovled