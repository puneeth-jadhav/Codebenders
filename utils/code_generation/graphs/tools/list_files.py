from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from langchain_core.runnables import RunnableConfig
import os

class ListFilesInput(BaseModel):
    path: str = Field(description="The relative directory path to list the contents of.")
    recursive: bool = Field(True, description="Whether to list contents recursively.")


def list_files(path: str, recursive: bool, config: RunnableConfig) -> str:
    excluded_folders = ["node_modules", "__pycache__", "env", "venv", 
                    "target/dependency", "build/dependencies", "dist",
                    "out", "bundle", "vendor", "tmp", "temp", "deps", 
                    "pkg", "Pods"]
    
    def recursive_traverse(current_dir, indent=0):
        structure_str = ""
        try:
            for entry in sorted(os.scandir(current_dir), key=lambda e: e.name):
                if entry.name in excluded_folders:
                    continue
                structure_str += " " * indent + entry.name + "\n"
                if entry.is_dir():
                    structure_str += recursive_traverse(entry.path, indent + 1)
        except PermissionError:
            pass
        return structure_str

    cwd = config['metadata'].get("base_path")
    
    if cwd is None:
        return "Base path doesn't exist."
    
    complete_path = cwd + path
    if recursive:
        return recursive_traverse(complete_path, 0)
    else:
        structure_str = ""
        try:
            for entry in sorted(os.scandir(), key=lambda e: e.name):
                if entry.name in excluded_folders:
                    continue
                structure_str += " " + entry.name + "\n"
        except PermissionError:
            pass
        return structure_str
    
list_files_tool = StructuredTool.from_function(
    func=list_files,
    name="list_files",
    description="Allows the LLM to list files and directories within a specified directory, optionally recursively.",
    args_schema=ListFilesInput,
    return_direct=False
)