# ✈️ VoyageCrew — Multi-Agent Travel Planner with MCP

An AI-powered travel planning application that transforms a natural-language trip request into a practical, structured travel plan. It combines a multi-agent workflow with Model Context Protocol (MCP) integrations to research flights, hotels, weather, and day-by-day itineraries in one place.

[Try VoyageCrew](https://a-multi-agent-travel-planner-with-mcp.onrender.com/)

## What it does

- Researches flight options and travel recommendations
- Suggests hotel stays based on destination and budget
- Retrieves weather information for travel dates
- Builds a structured itinerary for each day
- Uses a multi-agent workflow to turn inputs into a final travel response

## MCP integrations and travel workflow

The planner connects to three MCP servers to gather travel information:

- **Tavily** provides hotel research through its remote MCP endpoint: `https://mcp.tavily.com/mcp/`
- **AviationStack** runs as a local stdio MCP server using `uvx aviationstack-mcp` and supplies airport and airline information
- **Weather** runs as a local MCP server in `custom_weather_mcp_server.py` and provides current conditions and forecasts

The MCP client in `mcp_client.py` defines helpers for these integrations, including `tavily_mcp_search`, `aviation_mcp_call`, `weather_mcp_search`, and `forecast_mcp_search`. It also uses `extract_destination` to identify the destination from a user's request.

The agents in `agents.py` use these helpers to research flights, hotels, and weather, then generate an itinerary and final response. `backend.py` coordinates the agents in a LangGraph workflow.


## Setup

Clone the repo:
```bash
git clone https://github.com/TharushiDinushika/A-Multi-Agent-Travel-Planner-with-MCP.git
```

```bash
cd A-Multi-Agent-Travel-Planner-with-MCP
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

- Copy the contents of `.env.example` into a new file named `.env`
- Add your API keys and required credentials

Set up PostgreSQL:

- Download and install PostgreSQL: https://www.postgresql.org/download/
- Create a PostgreSQL database server on Render or another provider
- Connect to it using pgAdmin or your preferred database client

Run the application locally:

```bash
python app.py
```

## Project notes

This project is designed as a practical example of how MCP-enabled agents can collaborate to solve real-world travel planning tasks with structured data and AI-generated recommendations.

