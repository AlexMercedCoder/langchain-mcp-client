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

### If Using the Dremio MCP Server

[The Dremio MCP Server](https://github.com/dremio/dremio-mcp)

Follow the docs to configure the server, and the JSON to configure the client would look like:

```json
{
  "dremio": {
    "transport": "stdio",
    "command": "uv",
    "args": [
      "run",
      "--directory",
      "/absolute/path/to/dremio-mcp",  // update with your actual path
      "dremio-mcp-server",
      "run"
    ]
  }
}
```

[Demo of Using Dremio MCP Server with this Client](https://youtu.be/MFdKrjp5Kv4)

## Using Other Models

You can use any LangChain-compatible LLM. Just set the `LLM_MODEL` environment variable to the model you want to use.

```
########################################
# OpenAI (GPT-3.5, GPT-4, GPT-4o)
########################################
LLM_MODEL=openai:gpt-4.1
OPENAI_API_KEY=your-openai-api-key


########################################
# Anthropic (Claude 2, Claude 3 Opus/Sonnet/Haiku)
########################################
LLM_MODEL=anthropic:claude-3-opus-20240229
ANTHROPIC_API_KEY=your-anthropic-api-key


########################################
# Google (Gemini 1.5 Pro via Generative AI)
########################################
LLM_MODEL=google:gemini-pro
GOOGLE_API_KEY=your-google-genai-api-key


########################################
# Mistral (Mistral models hosted on mistral.ai)
########################################
LLM_MODEL=mistral:mistral-medium
MISTRAL_API_KEY=your-mistral-api-key


########################################
# Cohere (Command R+, etc.)
########################################
LLM_MODEL=cohere:command-r-plus
COHERE_API_KEY=your-cohere-api-key


########################################
# Together AI (Proxy for OSS models: Mixtral, Zephyr, LLaMA)
########################################
LLM_MODEL=together:mistralai/Mixtral-8x7B-Instruct-v0.1
TOGETHER_API_KEY=your-together-api-key


########################################
# Fireworks AI (Open-weight and commercial model access)
########################################
LLM_MODEL=fireworks:accounts/fireworks/models/llama-v2-13b-chat
FIREWORKS_API_KEY=your-fireworks-api-key


########################################
# Azure OpenAI (Azure-hosted GPT-4/3.5)
########################################
LLM_MODEL=azure:gpt-4
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/


########################################
# AWS Bedrock (Claude, Mistral, LLaMA, Cohere via AWS)
########################################
LLM_MODEL=bedrock:anthropic.claude-3-sonnet-20240229-v1:0
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
```