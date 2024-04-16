# Recursive Retrieval Updates
## Update 4/6/24
- LLM "Judge"
  - analyze quality of perplexity models (sonar-small-online, mistral, mixtral) on conciseness, informativeness, and accuracy
  - potential improvements should focus on quality of the prompt fed into GPT3.5 (or use GPT4)
  - results indicate sonar is best, but due to cost, mistral is best option for filling KG
- Incorporate Mistral model for external querying in streamlit app

## Update 3/21/24
- Custom synonym expansion
  - leveraging llm to produce larger range of synonyms of key entities found in query
  - custom formatting to fit neo4j
  - seems to dramatically improve web query &rarr; finding in graph afterwards using recursive retrieval
  - further testing to fine tune the prompt for increased accuracy

## Update 3/19/24
- Enhancing retrieval with llm
  - passing in llm to `KnowledgeGraphRAGRetriever` allows model to make jumps in entity extraction process (ie return entities not specifically mentioned)
    - ex. `query`: Tell me about Sirius Black. `entities`: ['Harry Potter'] (assuming Sirius Black is not an existing entity)
  - passing in llm to `RetrieverQueryEngine` allows model to directly mix in info from llm and KG in response
  - overall behavior is a bit nondeterministic
  - likely best to not use llm on either step in order to ensure information gets added to KG
- Custom entity extraction
  - under entity_extraction folder
  - work in progress - uses LangChain to pipe prompt (with template) &rarr; llm &rarr; pydantic json format
  - issue in custom function not being called, look into if there's time
- External querying using Perplexity now works
  - run entirety of external_perplexity.ipynb with new query
  - need to test effectiveness

## Update 3/14/24
- Set up querying of web corpus using Gemma, but through locally hosted model using Ollama
  - no API calls on external server that could be easily integrated with llama index frameworks
  - initial observation is that it is much slower to slower to locally host
  - Ollama can be used to host all of the open source models as well
  - very easy Ollama integration with llama index 
  - using https://docs.llamaindex.ai/en/latest/examples/llm/ollama.html

## Update 3/13/24
- Set up queyring of web corpus using Perplexity
  - really great optionality in specific model to use
    - mistral-7b-instruct
    - mixtral-8x7b-instruct
    - sonar-small-chat (perplexity model)
    - others found here: https://docs.perplexity.ai/docs/model-cards
  - interesting update from perplexity recently: *Deprecation and removal of codellama-34b-instruct and llama-2-70b-chat*
  - test results under /tests
- Overall querying external source and adding to KG is successful
- When using RAG retrieval, hard to identify key entities at times for newly added nodes
- Looking into why the retrieval process is a little buggy

## Update 3/12/24
- Set up querying of web corpus using Llama 2
  - information is succesfully injected into KG
  - when querying afterwards, RAG retreiver and index both have a hard time identifying the new topics being asked as key entities (index has some better luck)
- Looking into LangChain + Diffbot for alternative options
- Investigating why key entities are not being identified using llama index
- https://lmy.medium.com/comparing-langchain-and-llamaindex-with-4-tasks-2970140edf33