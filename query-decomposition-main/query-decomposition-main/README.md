# What is Query Decomposition?
Query Decomposition is a preprocessing technique in Large Language Models (LLMs) that simplifies complex queries into smaller, manageable sub-queries, enhancing the LLM's response effectiveness. This technique is applied only to complex queries, leaving simpler queries unchanged.

## Why Decompose a Query?
Decomposing queries allows the LLM to cover all aspects of a multifaceted user inquiry more effectively. By breaking down complex questions into simpler elements, the model can generate more accurate and comprehensive responses, synthesizing these to produce a final answer.

## Query Engine Overview
The Query Engine employs appending and fine-tuning within a LangChain framework, enhancing its capability to process queries efficiently.

## How It Works
Initial Setup: Initially implemented with a LlamaIndex finetuned approach, the engine was later optimized to use LangChain for its speed and ease of use.
Execution: Users can invoke the engine individually or in batches with pre-decomposed sets of queries.

 Define the engine
query_analyzer_with_examples = prompt.partial(examples=example_msgs) | llm_with_tools | parser

### Individual Invocation
sub_qs = query_analyzer_with_examples.invoke(
    {"question": "What is 2 + 2? Why is it not 3?"}
)

### Batch Invocation
questions = [
    "Where can I buy a macbook pro with M3 chip? What is the difference to the M2 chip? How much more expensive is the M3?",
    "How can I buy tickets to the upcoming NBA game? What is the price of lower bowl seats versus nosebleeds? What is the view like at either seat?",
    "Between a macbook and a windows machine, which is better for systems engineering? Which chips are most ideal? What is the price difference between the two?",
]

responses = []
for question in questions:
    responses.append(query_analyzer_with_examples.invoke({"question": question}))
    
## Role in the Larger System
The Query Engine acts as a conduit within a parallel system, passing all decomposed queries or the original query to the Routing Agent. It also sends the original query to the reranker to optimize the outputs from the Routing Agent.

## Future Contributions
Multiprocessing Integration: When a multiprocessing system is available, all inputted queries will be passed to the Query Decomposer, which will then route the appropriate (sub)queries to the Routing Agent for parallel processing.
Self-Learning: The system will append successfully decomposed queries to the engine's example store, enhancing its capability for future queries.

## Contributors
@arnavchopra1864
@aishwarya-balaji
