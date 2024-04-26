import os
from collections import defaultdict
from typing import List

from dotenv import load_dotenv
from llama_index.core.llms import ChatMessage
from llama_index.llms.perplexity import Perplexity
from pandas import DataFrame

from judge import custom_response_evaluator


def benchmark(
    model_name: str,
    data_points: List,
    conciseness: List,
    informativeness: List,
    accuracy: List,
):
    load_dotenv()
    pplx_api_key = os.getenv("PERPLEXITY_API_KEY")

    query_llm = Perplexity(api_key=pplx_api_key, model=model_name, temperature=0.5)
    base_prompt = "tell me about "

    for subject in data_points:
        query = base_prompt + subject
        messages_dict = [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": query},
        ]
        messages = [ChatMessage(**msg) for msg in messages_dict]
        response = query_llm.chat(messages)
        result = custom_response_evaluator(query, response)

        conciseness.append(result["conciseness"])
        informativeness.append(result["informativeness"])
        accuracy.append(result["accuracy"])
