# Retrieval Augmented Generation with Graph Knowledge Store

## Introduction

-   Used Neo4j Graph to store knowledge graph
-   Customized [Memory Stream](src/memory/memory_stream.py) to store entities of personal knowledge

## Installation

### Using conda env on Notebook

```
conda env create -n rag python=3.11
conda activate rag
pip install -r requirements.txt
conda install ipykernel
python -m ipykernel install --user --name=rag
jupyter notebook
```

### Run Streamlit Application

[README for Streamlit](streamlit_app/README.md)

## Update
- [2024/02/19](docs/update_021924.md)
- [2024/02/20](docs/update_022024.md)
- [2024/02/25](docs/update_022524.md)
- [2024/02/29](docs/update_022924.md)