from typing import TypedDict, Sequence
from langchain_core.messages import ToolMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolInvocation
import json

from .openai_models import OpenAIModel
from .tools import CodingTools

# Define the state
class GraphState(TypedDict):
    messages: Sequence[BaseMessage]
    base_path: str

class OpenAIGraph:

    def __init__(self, system_message: str, model_name: str):
        self.tool_executor = CodingTools.get_executable_tools()
        self.open_ai_model = OpenAIModel(system_message=system_message, model_name=model_name)

        self.model = self.open_ai_model.make_model()

        # Initializing the graph
        self.graph = StateGraph(GraphState)


    # Def the function that determines whether to continue or not 
    def should_continue(self, state):
        last_message = state["messages"][-1]
        # if there are no tool calls, then we finish 
        if "tool_calls" not in last_message.additional_kwargs:
            return "end"
        # If there is a Response tool call, then we finish
        elif last_message.additional_kwargs["tool_calls"][-1]["function"]["name"] == "AttemptCompletionInput":
            return "end"
        # Otherwise if there is, we continue
        else:
            return "continue"
    
    # Define the function that calls the model
    def call_model(self, state):
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": messages + [response]}
    
    # Define the function to execute tools
    def call_tool(self, state):
        messages = state["messages"]
        base_path = state["base_path"]
        last_message = messages[-1]
        # Tool invocation
        action = ToolInvocation(
            tool=last_message.additional_kwargs["tool_calls"][-1]["function"]["name"],
            tool_input=json.loads(
                last_message.additional_kwargs["tool_calls"][-1]["function"]["arguments"]
            ),
        )
        # We call the tool_executor and get back a response
        if action.tool == "write_to_file" or action.tool == "read_file" or action.tool == "list_files" or action.tool == "execute_command":
            response = self.tool_executor._execute(action, config={"base_path" : base_path})
        else:
            response = self.tool_executor._execute(action)
        # We use the response to create a FunctionMessage 
        tool_message = ToolMessage(content=str(response), name=action.tool, tool_call_id=last_message.additional_kwargs["tool_calls"][-1]["id"])
        # Now we add this to the list of tool nodes so it is maintained.
        return {"messages": messages + [tool_message]}


    def generate_graph(self):

        # Define the two Nodes we will cycle between
        self.graph.add_node("coding_llm", self.call_model)
        self.graph.add_node("tools_invocation", self.call_tool)

        # Setting the satrting node to thei point 
        self.graph.set_entry_point("coding_llm")

        # Set out Conditional Edges
        self.graph.add_conditional_edges(
            "coding_llm",
            self.should_continue,
            {
                "continue": "tools_invocation",
                "end": END
            }
        )

        # Setting normal edge
        self.graph.add_edge("tools_invocation", "coding_llm")

        # Compiling the graph
        self.app = self.graph.compile()

        return self.app