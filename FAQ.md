# Frequently Asked Questions (FAQ)

## General

### What is Memary?

Memary is **the open source memory layer for autonomous agents**. It emulates human memory to advance AI agents by tracking users' preferences, knowledge breadth, and knowledge depth over time.

### How does Memary work?

Memary integrates three core components:

1. **Knowledge Graphs** — Store entities and relationships from agent interactions
2. **Memory Stream** — Track all entities with timestamps (knowledge breadth)
3. **Entity Knowledge Store** — Track frequency and recency of entity references (knowledge depth)

These components work together to provide personalized, context-aware responses.

### How is Memary different from other agent frameworks?

Memary focuses **specifically on memory management**:

- **Memory Layer** — Not a full agent framework, but a memory system you integrate into existing agents
- **Knowledge Graphs** — FalkorDB/Neo4j graph databases for entity relationships
- **Human Memory Emulation** — Mimics how human memory evolves and learns over time

Use Memary with LlamaIndex, LangChain, or any agent framework to add persistent memory.

### What is the Memory Stream?

The **Memory Stream** captures all entities inserted into the Knowledge Graph with their timestamps:

- Reflects **knowledge breadth** (concepts users have exposure to)
- Enables timeline analysis of user interests
- Tracks evolution of user knowledge over time

### What is the Entity Knowledge Store?

The **Entity Knowledge Store** tracks frequency and recency of entity references:

- Reflects **knowledge depth** (concepts users are familiar with)
- Ranks entities by relevance (frequency + recency)
- Helps identify user expertise areas

## Getting Started

### How do I install Memary?

**With pip:**

```bash
pip install memary
```

**Locally:**

```bash
pip install -r requirements.txt
```

**Note:** Requires Python ≤ 3.11.9

### What models are supported?

Memary supports:

- **Ollama** — Llama 3 8B/40B (suggested defaults), LLaVA (vision)
- **OpenAI** — gpt-3.5-turbo, gpt-4-vision-preview

Default is locally run models unless explicitly specified.

### How do I run Memary?

```bash
cd streamlit_app
streamlit run app.py
```

### What credentials do I need?

Required credentials (in `.env`):

- `OPENAI_API_KEY` — For GPT models (optional if using Ollama)
- `PERPLEXITY_API_KEY` — For external queries
- `GOOGLEMAPS_API_KEY` — For location tool
- `ALPHA_VANTAGE_API_KEY` — For stocks tool
- `FALKORDB_URL` or `NEO4J_URL` + `NEO4J_PW` — For graph database

## Features

### What is the Routing Agent?

The **Routing Agent** is a ReAct agent implementation:

- Plans and executes queries using provided tools
- Uses Knowledge Graph search tool to retrieve information
- Falls back to external search if no related entities exist
- Includes vision (LLaVA) and location tools

### What is the Knowledge Graph?

The **Knowledge Graph** stores entities and relationships:

- Graph database (FalkorDB or Neo4j) for structured knowledge
- Uses Llama Index to add nodes from documents
- Perplexity for external queries
- Recursive retrieval + multi-hop reasoning for efficient search

### What is Multi-Graph?

**Multi-Graph** enables multiple agents with separate memory contexts:

- Create multiple graphs with different IDs
- Switch between agent memory contexts seamlessly
- Each agent has its own Knowledge Graph and Memory

### How do I add custom tools?

```python
def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b

chat_agent.add_tool({"multiply": multiply})
```

### How do I remove custom tools?

```python
chat_agent.remove_tool("multiply")
```

## Integration

### How do I integrate Memary into my agent?

```python
from memary.agent.chat_agent import ChatAgent

chat_agent = ChatAgent(
    "Personal Agent",
    memory_stream_json,
    entity_knowledge_store_json,
    system_persona_txt,
    user_persona_txt,
    past_chat_json,
)
```

Pass in subset of `['search', 'vision', 'locate', 'stocks']` as `include_from_defaults` for different default tools.

### Can I use Memary with other agent frameworks?

Yes! Memary is designed to integrate with any agent framework:

- **LlamaIndex** — Native integration (ReAct agent)
- **LangChain** — Use ChatAgent as tool
- **Custom agents** — Import memory modules separately

### How do I set up user personas?

Edit `streamlit_app/data/user_persona.txt` using the template in `streamlit_app/data/user_persona_template.txt`:

- Replace curly brackets with relevant information
- User persona shapes agent behavior and responses

## Configuration

### What environment variables are required?

Key environment variables (see `.env.example`):

- `OPENAI_API_KEY` — OpenAI API access
- `PERPLEXITY_API_KEY` — Perplexity API for external queries
- `GOOGLEMAPS_API_KEY` — Google Maps geocoding
- `ALPHA_VANTAGE_API_KEY` — Stock data
- `FALKORDB_URL` or `NEO4J_URL` + `NEO4J_PW` — Graph database

### How do I configure local models?

1. Install Ollama: `ollama pull llama3`
2. Run Ollama: `ollama serve`
3. Memary will auto-detect and use local models

### What databases are supported?

Memary supports:

- **FalkorDB** — Recommended (free tier available)
- **Neo4j** — Alternative (free tier available)

Both provide graph database functionality for Knowledge Graphs.

## Troubleshooting

### Memary won't install

**Common causes:**

1. **Python version too high**: Requires Python ≤ 3.11.9
2. **Missing dependencies**: Install requirements.txt
3. **Pip network issues**: Check internet connection

**Solution:**

```bash
# Check Python version
python --version

# Create correct virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install memary
```

### Streamlit app won't start

**Common causes:**

1. **Missing credentials**: Check `.env` file
2. **Database connection failed**: Verify FalkorDB/Neo4j URL
3. **Port conflicts**: Ensure port 8501 is available

**Solution:**

```bash
# Check environment
cat .env

# Test database connection
python -c "from memary.knowledge_graph import KnowledgeGraph; kg = KnowledgeGraph()"

# Run with verbose
streamlit run app.py --logger_level debug
```

### Knowledge Graph search returns empty

**Common causes:**

1. **No entities in graph**: Add documents or run queries first
2. **Database connection issue**: Check FalkorDB/Neo4j connection
3. **Query doesn't match entities**: Try different query terms

**Solution:**

```bash
# Check graph contents
curl $FALKORDB_URL/graphs

# Add initial documents
python -c "from memary.knowledge_graph import KnowledgeGraph; kg = KnowledgeGraph(); kg.add_documents(['doc.txt'])"
```

### Memory Stream not updating

**Common causes:**

1. **Agent not storing responses**: Check `write_back()` is called
2. **JSON file path incorrect**: Verify memory_stream_json path
3. **Permission issues**: Check file permissions

**Solution:**

```python
# Verify write_back is called
response = chat_agent.query(query)
chat_agent.write_back()  # Ensures KG writeback

# Check memory file
cat memory_stream.json
```

## Help & Resources

- **Documentation**: [memarydocs](https://kingjulio8238.github.io/memarydocs/)
- **Demo**: [YouTube Demo](https://youtu.be/GnUU3_xK6bg)
- **LinkedIn**: [Memary Labs](https://www.linkedin.com/company/memary/)
- **Twitter**: [@memary_labs](https://x.com/memary_labs)
- **PyPI**: [memary](https://pypi.org/project/memary/)
- **Issues**: [GitHub Issues](https://github.com/kingjulio8238/Memary/issues)

---

*Last updated: 2026-05-16*