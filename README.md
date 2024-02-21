# Retrieval Augmented Generation with Graph Knowledge Store

## Introduction

-   Used Nebula Graph to store knowledge graph
-   Utilized [chat memory buffer](https://docs.llamaindex.ai/en/latest/examples/chat_engine/chat_engine_context.html#chat-engine-context-mode) function for memory stream (TBD)

## Installation

### Nebula Graph Docker-Compose
- [Quickly deploy NebulaGraph using Docker](https://docs.nebula-graph.io/3.6.0/2.quick-start/1.quick-start-workflow/#quickly_deploy_nebulagraph_using_docker)
- run `curl -fsSL nebula-up.siwei.io/install.sh | bash`


### Using conda env on Notebook

```
conda env create -n rag python=3.11
conda activate rag
pip install -r requirements.txt
conda install ipykernel
python -m ipykernel install --user --name=rag
jupyter notebook
```

## Update
- [2024/02/19](docs/update_021924.md)