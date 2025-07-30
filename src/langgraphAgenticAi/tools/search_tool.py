from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode

def get_tools():
    """
    Return the list of tools to be used in the chatbot
    """
    tools = [TavilySearch(max_results=2)]

    return tools

def create_tool_node(tools):
    """
    Creates a tool node using the available tools and returns for the graph
    """

    return ToolNode(tools)
