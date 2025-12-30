# Universal MCP Chat Client

A robust Python client for interacting with **Model Context Protocol (MCP)** servers. Built with **LangChain** and **LangGraph**, it enables you to chat with multiple MCP servers simultaneously using a natural language interface on the CLI or a Web UI.

![Universal MCP Client](https://github.com/user-attachments/assets/placeholder)

## Features
-   **Multi-Server Support**: Connect to unlimited MCP servers (local processes or remote HTTP/SSE).
-   **Secure Authentication**: Securely inject API keys and OAuth tokens via Environment Variables (`${VAR}`).
-   **Streaming Responses**: Real-time token-by-token generation in the CLI.
-   **Customizable Agent**: Configure the System Prompt and LLM Provider via `.env`.
-   **Web Interface**: Optional Flask-based UI for browser interaction.
-   **Dremio Integration**: Native helper script for Dremio OAuth flow.

---

## Quickstart

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/AlexMercedCoder/langchain-mcp-client.git
cd langchain-mcp-client
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Edit `.env` to add your LLM API Key (e.g., OpenAI):
```env
OPENAI_API_KEY=sk-...
LLM_MODEL=openai:gpt-4o
SYSTEM_PROMPT="You are a helpful assistant."
```

### 3. Run the Client
Start the interactive CLI:
```bash
python client.py
```

---

## Configuration Scenarios

Define your servers in `mcp_servers.json`.

### Scenario 1: Local Tools (Python/Node/Binaries)
Connect to local processes using the `stdio` transport. Ideal for secure, local-only tools like filesystem access or SQLite interaction.

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/files"],
    "transport": "stdio"
  },
  "sqlite": {
    "command": "uvx",
    "args": ["mcp-server-sqlite", "--db-path", "./my.db"],
    "transport": "stdio"
  }
}
```

### Scenario 2: Remote / Public Servers
Connect to public MCP servers via HTTP.

```json
{
  "weather": {
    "url": "https://weather-mcp.example.com",
    "transport": "streamable_http"
  }
}
```

### Scenario 3: Secure / Authenticated Servers
**Never commit secrets to `mcp_servers.json`.**
Instead, use the `${VAR_NAME}` syntax. The client will automatically substitute these with values from your `.env` file at runtime.

**In `.env`:**
```env
MY_OAUTH_TOKEN=secret-123
```

**In `mcp_servers.json`:**
```json
{
  "secure-api": {
    "url": "https://api.example.com/mcp",
    "transport": "streamable_http",
    "headers": {
      "Authorization": "Bearer ${MY_OAUTH_TOKEN}"
    }
  }
}
```

### Scenario 4: Dremio Integration (OAuth 2.0)
To query Dremio Data Catalogs, you must authenticate via OAuth.

1.  **Create App**: In Dremio, register a "Native" OAuth App with Redirect URI:
    `http://localhost:8000/callback`
2.  **Configure `.env`**:
    ```env
    DREMIO_CLIENT_ID=your-client-id
    ```
3.  **Get Token**: Run the helper script:
    ```bash
    python auth_dremio.py
    ```
    Login via the browser link provided.
4.  **Save Token**: Copy the resulting token to `.env`:
    ```env
    DREMIO_TOKEN=eyJhbGci...
    ```
5.  **Configure Server**:
    ```json
    "dremio": {
      "url": "https://mcp.dremio.cloud/mcp/<PROJECT_ID>",
      "transport": "streamable_http",
      "headers": {
        "Authorization": "Bearer ${DREMIO_TOKEN}"
      }
    }
    ```

---

## Advanced Features

### System Prompts
Customize the agent's personality or rules by setting `SYSTEM_PROMPT` in `.env`.
```env
SYSTEM_PROMPT="You are a SQL expert. Always check schemas before querying."
```

### Web Interface
Prefer a browser UI?
```bash
python webui.py
```
Open `http://localhost:5000` to chat.

### Switching LLM Providers
The client uses LangChain, so it supports OpenAI, Anthropic, Google Vertex, etc.
Change `LLM_MODEL` in `.env`:
- `openai:gpt-4o`
- `anthropic:claude-3-sonnet` (requires `ANTHROPIC_API_KEY`)
- `google:gemini-pro` (requires `GOOGLE_API_KEY`)

---

## Development

### Upgrade Dependencies
Keep the core libraries up to date:
```bash
pip install --upgrade -r requirements.txt
```

### Verification
Run tests to ensure environment substitution and agent creation are working:
```bash
python verify_changes.py
```

## License
MIT