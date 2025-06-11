# 🧠 Universal MCP Chat Client

This is a chat-based CLI tool that connects to multiple [FastMCP](https://gofastmcp.com) servers and lets you invoke their tools through natural language using [LangChain](https://python.langchain.com/) and [LangGraph](https://www.langgraph.dev/).

Supports:
- ✅ Environment-based credentials and model config
- ✅ JSON-based multi-server configuration
- ✅ Chat loop using any LangChain-compatible LLM
- ✅ Easily pluggable FastMCP tool servers

---

## 📦 Features

- Connects to multiple MCP tool servers via `stdio` or `streamable-http`
- Uses LangChain's ReAct agent to interpret prompts and choose tools
- Loads credentials and model via `.env`
- Runs in a simple terminal environment with rich CLI display

---

## 🚀 Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/AlexMercedCoder/langchain-mcp-client
cd langchain-mcp-client
```

### 2. Install Dependencies
We recommend using a virtual environment.

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install python-dotenv langchain langgraph langchain-mcp-adapters fastmcp openai rich langchain-openai
```

### 3. Configure Your Environment
Create a `.env` file in the root:

```env
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=openai:gpt-4.1
DETAILED_OUTPUT=false #change to true if want full message history object
```

### 4. Define Your MCP Servers
Edit the `mcp_servers.json` file:

```json
{
  "math": {
    "command": "python",
    "args": ["./mcp_servers/math_server.py"],
    "transport": "stdio"
  },
  "weather": {
    "url": "http://localhost:8000/mcp/",
    "transport": "streamable_http"
  }
}
```
You can point to any local or remote MCP server using:

stdio (for local processes)

streamable_http (for web APIs)

### 5. Start Sample MCP Servers
In one terminal, start the weather server:

```bash
python weather_server.py
```

In another terminal, start the math server:

```bash
python math_server.py
```

### 6. Run the Chat Client

```bash
python client.py
```

You’ll be dropped into a chat loop. Try asking:

```python-repl
>>> what is (3 + 5) x 12?
>>> what's the weather in Paris?
```

### 🛠 Adding Your Own Tools
Create a new FastMCP server, e.g. `mcp_servers/my_tools_server.py`:

```python
from fastmcp import FastMCP

mcp = FastMCP("MyTools")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Add it to mcp_servers.json:

```json
"mytools": {
  "command": "python",
  "args": ["./my_tools_server.py"],
  "transport": "stdio"
}
```

Restart `client.py`, and you're good to go!

### 📁 File Structure
```graphql
.
├── .env                     # Your API key and model configuration
├── client.py                # Main CLI application
├── mcp_servers/             # Folder containing sample MCP server implementations
│   ├── math_server.py       # Stdio server with math tools
│   └── weather_server.py    # HTTP server with weather tools
├── mcp_servers.json         # MCP server connection configuration
├── requirements.txt         # Python dependencies
```