from flask import Flask, render_template, request, jsonify
import asyncio
import json
import os
from dotenv import load_dotenv
from rich.console import Console

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Import shared env setup logic
from env_setup import setup_llm_environment

# Load .env variables
load_dotenv()

# Flask app and console setup
app = Flask(__name__)
console = Console()

# Cache the agent instance globally so it only loads once
agent_cache = {}

# Home route – serves the HTML page
@app.route("/")
def index():
    return render_template("webui.html")

# Chat route – handles AJAX requests from frontend
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    try:
        # Lazy-load and cache the agent
        if "agent" not in agent_cache:
            console.print("[blue]Loading LLM agent...[/blue]")
            llm_model = setup_llm_environment()
            with open("mcp_servers.json", "r") as f:
                server_config = json.load(f)
            client = MultiServerMCPClient(server_config)
            tools = asyncio.run(client.get_tools())
            agent_cache["agent"] = create_react_agent(llm_model, tools)

        agent = agent_cache["agent"]
        response = asyncio.run(agent.ainvoke({"messages": user_input}))

        # Extract final message content
        messages = response.get("messages", [])
        final_message = next((msg.content for msg in reversed(messages) if msg.type == "ai"), None)

        return jsonify({"response": final_message or "No AI response found."})

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
