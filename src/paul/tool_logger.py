from langchain.callbacks.base import BaseCallbackHandler
from collections import Counter

class ToolLogger(BaseCallbackHandler):
    def __init__(self):
        self.counts = Counter()     # Holds the count of how many times each tool has been called 
        self.calls = []             # A list that records each tool call as a tuple: (tool name, tool input string)

    def on_tool_start(self, serialized, input_str, **kwargs):
        name = serialized['name']               # Get the name of the tool being called
        self.counts[name] += 1                  # Increment its count
        self.calls.append((name, input_str))    # Record the call with its input string