import os
from typing import Dict

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import OpenAI

from output import Output

# TODO: Try inserting into the template some examples of queries and responses that user would personally give scores of x, y, z to.

def custom_response_evaluator(query: str, response: str) -> Dict[str, int]:
    load_dotenv()
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_KEY"), temperature=0)
    parser = JsonOutputParser(pydantic_object=Output)

    template = """
    You are an expert response judger. Score the provided respose a score from 0 to 1000 with 0 being the worst and 1000 being the best.
    Give separate scores for conciseness, informativeness and accuracy.
    For conciceness, focus on how succinct the response is and how clearly the information is conveyed using minimal words.
    For informativeness, focus on how comprehensive and relevant the contents of the response is to the given query.
    For accuracy, focus on the correctness and decree of preciseness that the response has.
    Hold the scores you give to the highest quality with higher numbers given only to the best of the best.
    
    Format: {format_instructions}

    Query: {query}
    Response: {response}
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["query", "response"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    result = chain.invoke({"query": query, "response": response})
    return result
