import os
import certifi
import asyncio
from dotenv import load_dotenv
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from mcp_client import tavily_mcp_search
from tools.flight_tool import search_flights
import json

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is misssing. Please add it to your .env file.")

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_PROMPT_RESULT_CHARS = 5000

llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    max_tokens=3000,
)


class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: str


def _to_text(result) -> str:
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        if "text" in result:
            return str(result["text"])
        return json.dumps(result, ensure_ascii=False)
    if isinstance(result, (list, tuple)):
        return "\n".join(_to_text(item) for item in result)
    return str(result)


def _bounded_prompt_result(result) -> str:
    result = _to_text(result)

    if len(result) <= MAX_PROMPT_RESULT_CHARS:
        return result

    truncated = result[:MAX_PROMPT_RESULT_CHARS].rsplit(" ", 1)[0]
    return f"{truncated}\n[Additional search results omitted to keep the prompt within limits.]"


def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)

    return {
        "flight_results": flight_data,
        "messages": [AIMessage(content="Flight results fetched.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


async def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"
    hotel_results = _to_text(await tavily_mcp_search(query))

    return {
        "hotel_results": hotel_results,
        "messages": [AIMessage(content="Hotel information fetched.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def itinerary_agent(state: TravelState):
    prompt = f"""
Create a complete travel itinerary.

User Query:
{state['user_query']}

Flight Results:
{_bounded_prompt_result(state['flight_results'])}

Hotel Results:
{_bounded_prompt_result(state['hotel_results'])}

Make the itinerary practical, budget-aware, and easy to follow.
"""

    response = llm.invoke(
        [
            SystemMessage(content="You are an expert travel planner."),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def final_agent(state: TravelState):
    final_prompt = f"""
Generate the final travel response for the user.

User Request:
{state['user_query']}

Flights:
{_bounded_prompt_result(state['flight_results'])}

Hotels:
{_bounded_prompt_result(state['hotel_results'])}

Itinerary:
{_bounded_prompt_result(state['itinerary'])}

Format the final answer beautifully using these sections:

1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day-by-Day Itinerary
5. Estimated Budget
6. Final Recommendations

Important:
- Be clear and practical.
- Mention that live flight API may not provide ticket prices if pricing is unavailable.
- Keep the response useful for real travel planning.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content="You are a professional AI travel booking assistant."
            ),
            HumanMessage(content=final_prompt),
        ]
    )

    return {"messages": [response], "llm_calls": state.get("llm_calls", 0) + 1}
