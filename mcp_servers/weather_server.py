# weather_server.py
from fastmcp import FastMCP
import datetime

mcp = FastMCP("Weather Server")

@mcp.tool
async def get_weather(location: str) -> str:
    """Returns weather for the given location."""
    now = datetime.datetime.now()
    return f"The weather in {location} is sunny as of {now.strftime('%H:%M:%S')}."

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")
