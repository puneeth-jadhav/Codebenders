from pydantic import BaseModel, Field
from langchain.tools import StructuredTool

class AskFollowupQuestionInput(BaseModel):
    question: str = Field(description="The question the LLM wants to ask the user.")

def ask_followup_question(question: str) -> str:
    user_response = input(question)
    return f"User response: {user_response}"

ask_followup_question_tool = StructuredTool.from_function(
    func=ask_followup_question,
    name="ask_followup_question",
    description="Enables the LLM to ask the user a follow-up question and receive their input.",
    args_schema=AskFollowupQuestionInput,
    return_direct=False
)