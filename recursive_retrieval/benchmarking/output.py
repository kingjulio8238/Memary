from langchain_core.pydantic_v1 import BaseModel, Field


class Output(BaseModel):
    conciseness: int = Field(
        description="Score for how concise the response is from 0 to 1000 witih 0 being the worst and 1000 being the best."
    )
    informativeness: int = Field(
        description="Score for how informative the response is from 0 to 1000 witih 0 being the worst and 1000 being the best."
    )
    accuracy: int = Field(
        description="Score for how accurate the response is based on the question from 0 to 1000 witih 0 being the worst and 1000 being the best."
    )
