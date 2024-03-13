# Recursive Retrieval Updates
## Update 3/13/24
- Set up queyring of web corpus using Perplexity
  - really great optionality in specific model to use
    - mistral-7b-instruct
    - pplx-7b-chat-alpha
  - interesting update from perplexity recently: *Deprecation and removal of codellama-34b-instruct and llama-2-70b-chat*

## Update 3/12/24
- Set up querying of web corpus using Llama 2
  - information is succesfully injected into KG
  - when querying afterwards, RAG retreiver and index both have a hard time identifying the new topics being asked as key entities (index has some better luck)
- Looking into LangChain + Diffbot for alternative options
- Investigating why key entities are not being identified using llama index
- https://lmy.medium.com/comparing-langchain-and-llamaindex-with-4-tasks-2970140edf33