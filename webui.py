from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import asyncio
import json
import os
from dotenv import load_dotenv
from rich.console import Console

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from env_setup import setup_llm_environment, substitute_env_vars

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
console = Console()

# Secret key for sessions (required by Flask)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
app.config["SESSION_TYPE"] = "filesystem"  # stores session data in temporary files
Session(app)  # enable Flask session handling

# Cache the agent instance
agent_cache = {}

@app.route("/")
def index():
    # Initialize chat history if not present
    if "chat_history" not in session:
        session["chat_history"] = []
    return render_template("webui.html", chat_history=session["chat_history"])

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    try:
        # Load and cache the agent
        if "agent" not in agent_cache:
            console.print("[blue]Loading agent...[/blue]")
            llm_model = setup_llm_environment()
            with open("mcp_servers.json", "r") as f:
                server_config = json.load(f)
            # Substitute env vars
            server_config = substitute_env_vars(server_config)
            
            client = MultiServerMCPClient(server_config)
            tools = asyncio.run(client.get_tools())
            
            system_prompt = os.getenv("SYSTEM_PROMPT")
            agent_cache["agent"] = create_agent(llm_model, tools, system_prompt=system_prompt)

        agent = agent_cache["agent"]

        # Add user message to chat history
        session.setdefault("chat_history", []).append({"role": "user", "content": user_input})

        # Get response from agent
        response = asyncio.run(agent.ainvoke({"messages": user_input}))
        messages = response.get("messages", [])
        final_message = next((msg.content for msg in reversed(messages) if msg.type == "ai"), "No AI response found.")

        # Add assistant message to chat history
        session["chat_history"].append({"role": "agent", "content": final_message})
        session.modified = True  # mark session as changed

        return jsonify({"response": final_message})

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset_chat():
    session["chat_history"] = []
    session.modified = True
    return jsonify({"message": "Chat history cleared."})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
