from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from typing import List
import os
from entity_extraction.output import Output
from dotenv import load_dotenv

def custom_entity_extract_fn(query: str):
    return ["Harry potter"]
    load_dotenv()
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_KEY"), temperature=0)
    parser = JsonOutputParser(pydantic_object=Output)

    template = """
    You are an expert entity extraction system. Extract the following entities from the given text:
    
    Format: {format_instructions}

    Text: {query}
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    result = chain.invoke({"query": query})

    l = []
    for category in result:
        for entity in result[category]:
            l.append(entity)

    return l


# testing
# print(custom_entity_extract_fn("who is harry potter"))
