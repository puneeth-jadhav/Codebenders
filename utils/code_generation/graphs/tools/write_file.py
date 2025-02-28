from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from langchain_core.runnables import RunnableConfig
import os

class WriteToFileInput(BaseModel):
    path: str = Field(description="The relative path to the file where content should be written.")
    content: str = Field(description="The content to be written to the file.")


def write_to_file(path: str, content: str, config: RunnableConfig) -> str:
    cwd = config['metadata'].get("base_path")
    
    if cwd is None:
        return "Base path doesn't exist."

    complete_path = cwd + '/' +path
    
    # Check if directory exists, create if not
    if not os.path.exists(os.path.dirname(complete_path)):
        os.makedirs(os.path.dirname(complete_path))

    with open(complete_path, 'w') as f:
        f.write(content)
    f.close()
    return f"Wrote contents to {path}."
    
write_to_file_tool = StructuredTool.from_function(
    func=write_to_file,
    name="write_to_file", 
    description="Allows the LLM to create a new file or modify an existing one by writing specified content to a given file path.",
    args_schema=WriteToFileInput,
    return_direct=False
)

