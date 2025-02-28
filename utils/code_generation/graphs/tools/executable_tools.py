from .write_file import write_to_file_tool
from .read_file import read_file_tool
from .list_files import list_files_tool
from .execute_command import execute_command_tool
from .ask_followup_question import ask_followup_question_tool
from langgraph.prebuilt import ToolExecutor


class CodingTools:

    def __init__(self):
        pass
    
    @staticmethod
    def get_tools():
        return [
            write_to_file_tool,
            read_file_tool,
            list_files_tool,
            execute_command_tool,
            ask_followup_question_tool
        ]
    
    @staticmethod
    def get_executable_tools():

        tools = [
            write_to_file_tool,
            read_file_tool,
            list_files_tool,
            execute_command_tool,
            ask_followup_question_tool
        ]

        return ToolExecutor(tools)