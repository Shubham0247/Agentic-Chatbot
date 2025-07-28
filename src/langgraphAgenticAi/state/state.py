from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import Annotated,List

class State(TypedDict):
    """
    Represent the structure of the state used in graph
    """
    messages: Annotated[List, add_messages]