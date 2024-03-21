from typing import List

from langchain_core.pydantic_v1 import BaseModel, Field


class Output(BaseModel):
    synonyms: List[str] = Field(description="Synonyms of keywords provided, make every letter lowercase except for the first letter")
    # capitalization: List[str] = Field(description="Formatted keywords and synonyms with only the first letter of first word capitalized")
