url = ""

import os
import asyncio
import certifi
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
        },
        "aviationstack": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["aviationstack-mcp"],
            "env": {"AVIATION_STACK_API_KEY": AVIATIONSTACK_API_KEY},
        },
    }
)


# async def get_all_tools():
#     tools = await client.get_tools()
#     print("\nAvailable MCP Tools\n")

#     for tool in tools:
#         print(tool.name)


tavily_search_tool = None
avaiation_tools = {}


async def initialize_mcp():
    global tavily_search_tool
    global avaiation_tools

    if tavily_search_tool is not None and avaiation_tools:
        return

    tools = await client.get_tools()

    print("\nAvailabale MCP Tools\n")

    for tool in tools:
        print(tool.name)

    search_tool = next(tool for tool in tools if tool.name == "tavily_search")

    aviation_tools = {tool.name: tool for tool in tools if tool.name != "tavily_search"}


# tavily


async def get_tavily_search_tool():
    global tavily_search_tool
    if tavily_search_tool is not None:
        return

    tools = await client.get_tools()
    print("\nAvailable MCP Tools:")

    for tool in tools:
        print(tool.name)

    tavily_search_tool = next(tool for tool in tools if tool.name == "tavily_search")


async def tavily_mcp_search(query: str):
    await get_tavily_search_tool()
    result = await tavily_search_tool.ainvoke({"query": query})
    return result


# aviation stack


async def aviation_mcp_call(tool_name: str, tool_args: dict = None):
    tools = await client.get_tools()

    tool = next(t for t in tools if t.name == tool_name)

    result = await tool.ainvoke(tool_args or {})

    return result
