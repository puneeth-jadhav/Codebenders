from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from langchain_core.runnables import RunnableConfig
import subprocess

class ExecuteCommandInput(BaseModel):
    command: str = Field(description="The shell command to execute.")

def execute_command(command: str, config: RunnableConfig) -> str:
    base_path = config['metadata'].get('base_path')

    if command.find(base_path) == -1:
        command = "cd {base_path} && " + command

    command_result = subprocess.getoutput(command)
    return f"Result upon execution: {command_result}"    

execute_command_tool = StructuredTool.from_function(
    func=execute_command,
    name="execute_command",
    description="Allows the LLM to execute shell commands on the system.",
    args_schema=ExecuteCommandInput,
    return_direct=False
)