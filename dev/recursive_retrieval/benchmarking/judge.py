import os
from typing import Dict

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import OpenAI

from output import Output


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

    Here is an example: Given the query "tell me about harry potter", and the given response Harry Potter is a series of seven fantasy novels written by British author J.K. Rowling. The novels chronicle the life of a young wizard named Harry Potter and his friends Hermione Granger and Ron Weasley, who are all students at the Hogwarts School of Witchcraft and Wizardry.
    The series follows Harry's life from age 11 to 17. In the first book, Harry learns that his parents were killed by the dark wizard Lord Voldemort when Harry was a baby, and that Harry survived the attack with a lightning-shaped scar on his forehead. Harry then begins attending Hogwarts, where he makes friends, encounters professors like Severus Snape, and faces off against Voldemort and his followers.
    The Harry Potter books have been massively popular, spawning a highly successful film series that ran from 2001 to 2011, as well as a play, video games, theme park attractions, and a vast amount of fan fiction.
    The series is considered a landmark of 20th and 21st century children's literature.
    In summary, Harry Potter is a beloved fantasy series that has had a tremendous cultural impact through its books, films, and expanded universe.
    
    The judge should give a score of 300 for conciseness, 600 to informativeness, 900 for accuracy.
    
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
