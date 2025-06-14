from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph
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


def build_graph(tools : list[Callable], llm : ChatOpenAI) -> CompiledStateGraph:
    """Builds and returns a simple ReAct graph.

    Args:
        tools (list[Callable]): A list of tools that the LLM will have access to.
        llm (ChatOpenAI): The LLM that will be used.
    
    Returns:
        CompiledStateGraph: The compiled ReAct graph with the LLM and the tools.
    """
    # Bind the LLM with the given tools
    llm_with_tools = llm.bind_tools(tools)

    # Graph will store State class objects in each node
    graph = StateGraph(State)

    # Prompt Node
    def prompt_node(state : State) -> State:
        """Invokes the model.

        Args:
            state (State): The current state.
        
        Returns:
            State: A new state that occurs after invoking the model. The message of the new state will be appended to the message history
        """

        chat_history = state["messages"]
        new_message = llm_with_tools.invoke(chat_history)
        return {"messages" : [new_message]}
    graph.add_node("prompt_node", prompt_node)
    graph.set_entry_point("prompt_node")

    # Tool Node
    tool_node = ToolNode(tools)
    graph.add_node("tool_node", tool_node)
    graph.add_edge("tool_node", "prompt_node")

    # Conditional Edge
    def conditional_edge(state : State) -> Literal['tool_node', '__end__']:
        """Determines the next step in the graph.

        Args:
            state (State): The current state.
        
        Returns:
            Literal['tool_node', '__end__']: The next node to transition to.
        """
        # If the last message contained a tool call we need to route to the tool node
        chat_history = state["messages"]
        last_message = chat_history[-1]
        if last_message.tool_calls:
            return "tool_node"
        # Otherwise, the workflow ends
        else:
            return "__end__"
    graph.add_conditional_edges(
        'prompt_node',
        conditional_edge
    )
    APP = graph.compile()
    return APP