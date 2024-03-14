# Recursive Retrieval Updates
## Update 3/14/24
- Set up querying of web corpus using Gemma, but through locally hosted model using Ollama
  - no API calls on external server that could be easily integrated with llama index frameworks
  - initial observation is that it is much slower to slower to locally host
  - Ollama can be used to host all of the open source models as well
  - very easy Ollama integration with llama index 

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