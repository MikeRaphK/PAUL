from functools import partial

from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from typing import Annotated, Callable, Literal
from typing_extensions import TypedDict



# TypedDict is used to create a dictionary with explicitly defined key-value types.
# Each state will essentially be repressented as a pre-defined dictionary
class State(TypedDict):
    # Annotated is a special type hinting feature that allows attaching metadata to type hints without altering the actual type
    # For example:
    # def process(x: Annotated[int, "Must be a positive integer"]):
    #   print(x)
    # Python ignores "Must be a positive integer" at runtime, but libraries (like pydantic, langgraph, etc.) can read this metadata.

    # The add_messages reducer function is used to append new messages to the list instead of overwriting it. 
    # By default, keys without a reducer annotation will overwrite previous values. 
    messages : Annotated[list, add_messages]



def invoke_llm(state : State, llm_with_tools: Callable) -> State:
    """
    Invokes the model.

    Args:
        state (State): The current state.
    
    Returns:
        State: A new state that occurs after invoking the model. The message of the new state will be appended to the message history
    """

    chat_history = state["messages"]
    new_message = llm_with_tools.invoke(chat_history)
    return {"messages" : [new_message]}



def need_tool(state : State) -> Literal['Need tool', 'Done']:
    """
    Determines whether the agent needs a tool or not.

    Args:
        state (State): The current state.
    
    Returns:
        Literal['Need tool', 'Done']: The next node to transition to.
    """
    # If the last message contained a tool call we need to route to the tool node
    chat_history = state["messages"]
    last_message = chat_history[-1]
    if last_message.tool_calls:
        return "Need tool"
    # Otherwise, the workflow ends
    else:
        return "Done"


def build_react_graph(tools : list[Callable], llm : ChatOpenAI, png_path: str) -> CompiledStateGraph:
    """
    Builds and returns a simple ReAct graph.

    Args:
        tools (list[Callable]): A list of tools that the LLM will have access to.
        llm (ChatOpenAI): The LLM that will be used.
        png_path (str): The file path where the generated graph PNG image will be saved.
    
    Returns:
        CompiledStateGraph: The compiled ReAct graph with the LLM and the tools.
    """
    # Bind the LLM with the given tools
    llm_with_tools = llm.bind_tools(tools)

    # Graph will store State class objects in each node
    graph = StateGraph(State)

    # Entry point
    graph.add_node("ReAct agent", partial(invoke_llm, llm_with_tools=llm_with_tools))
    graph.set_entry_point("ReAct agent")

    # Toolkit
    graph.add_node("Toolkit", ToolNode(tools))
    graph.add_edge("Toolkit", "ReAct agent")

    # ReAct agent conditional Edge
    graph.add_conditional_edges(
        'ReAct agent',
        need_tool,
        {"Need tool": "Toolkit", "Done": END}
    )

    # Compile graph and write png
    APP = graph.compile()    
    img = APP.get_graph().draw_mermaid_png()
    with open(png_path, "wb") as f:
        f.write(img)
        print(f"Graph written to '{png_path}'\n")

    return APP