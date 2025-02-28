from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from langchain_core.runnables import RunnableConfig
import os

class ReadFileInput(BaseModel):
    path: str = Field(description="The relative path to the file to be read.")

def read_file(path: str, config: RunnableConfig) -> str:
    cwd = config['metadata'].get("base_path")
    
    if cwd is None:
        return "Base path doesn't exist."
    
    complete_path = cwd + '/' + path
    if(os.path.exists(complete_path)):
        with open(complete_path, 'r') as f:
            contents = f.read()
        return contents
    else:
        return "The file you are looking for doesn't exist."
    
read_file_tool = StructuredTool.from_function(
    func=read_file,
    name="read_file",
    description="Enables the LLM to read the content of a file from a specified path.",
    args_schema=ReadFileInput,
    return_direct=False
)