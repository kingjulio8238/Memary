from typing import List

from langchain_core.pydantic_v1 import BaseModel, Field


class Output(BaseModel):
    person: List[str] = Field(description="Names of people")
    organization: List[str] = Field(description="Names of companies or organizations")
    location: List[str] = Field(description="Names of locations or places")
    objects: List[str] = Field(description="Names of tangible thigns")
