import os
from collections import defaultdict

from dotenv import load_dotenv
from llama_index.core.llms import ChatMessage
from llama_index.llms.perplexity import Perplexity
from pandas import DataFrame

from judge import custom_response_evaluator

load_dotenv()
pplx_api_key = os.getenv("PERPLEXITY_API_KEY")

query_llm = Perplexity(
    api_key=pplx_api_key, model="sonar-small-online", temperature=0.5
)

data_points = [
    "harry potter",
    "dumbledore",
    "snape",
    "voldemort",
    "the deathly hallows",
    "the infinity stones",
    "crypto",
    "ut austin",
    "llms",
    "lions",
]


def benchmark():
    base_prompt = "tell me about "
    results = defaultdict(list)

    for subject in data_points:
        query = base_prompt + subject
        messages_dict = [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": query},
        ]
        messages = [ChatMessage(**msg) for msg in messages_dict]
        response = query_llm.chat(messages)
        result = custom_response_evaluator(query, response)

        for score in result:
            results[subject].append(result[score])

    print(results)


benchmark()
