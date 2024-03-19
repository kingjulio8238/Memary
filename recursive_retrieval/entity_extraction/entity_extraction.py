from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


def custom_entity_extract_fn(query: str) -> List[Dict[str, str]]:
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_KEY"), temperature=0)
    
    template = """
    You are an expert entity extraction system. Extract the following entities from the given text:
    - PERSON: Names of people
    - ORGANIZATION: Names of companies or organizations
    - LOCATION: Names of locations or places
    - OBJECTS: Names of tangible things
    
    Provide the extracted entities in the following JSON format:
    [
        {{
            "entity_type": "PERSON",
            "entity_value": "Extracted person name"
        }},
        {{
            "entity_type": "ORGANIZATION",
            "entity_value": "Extracted organization name"
        }},
        ...
    ]
    
    Text: {query}
    
    Extracted Entities:
    """
    
    prompt = PromptTemplate(template=template, input_variables=["query"])
    chain = LLMChain(llm=llm, prompt=prompt)
    
    result = chain.invoke(query)
    entities = eval(result)
    
    return entities