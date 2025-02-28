from pydantic import BaseModel, Field

class AttemptCompletionInput(BaseModel):
    """Final answer to the user"""
    result: str = Field(description="A brief description of what is developed in the project.")
    command: str = Field(description="A shell command to execute before finalizing the result.")