# === Import standard and external libraries ===

import json
import os
import asyncio
import re
from dotenv import load_dotenv
from rich.console import Console

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

# Import the central environment setup logic
from env_setup import setup_llm_environment, substitute_env_vars

# Create a Rich console for styled terminal output
console = Console()

# Load environment variables from .env file (e.g., API keys, model name)
load_dotenv()

# Detailed Output Flag (optional output verbosity)
detailed_output = os.getenv("DETAILED_OUTPUT", "false").lower() == "true"



# === Define the main asynchronous function ===
async def main():
    try:
        # Run validation + provider-specific env var setup
        llm_model = setup_llm_environment()
        console.print(f"[green]Using model:[/green] {llm_model}")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        return

    # Load the list of MCP servers from a local JSON file
    with open("mcp_servers.json", "r") as f:
        server_config = json.load(f)

    # Substitute environment variables in the server config
    server_config = substitute_env_vars(server_config)

    # Create a MultiServer MCP client using the server definitions from the JSON
    client = MultiServerMCPClient(server_config)

    # Use the client to retrieve and load all available MCP tools
    tools = await client.get_tools()

    # Create a LangChain + LangGraph ReAct-style agent with the given model and tools
    system_prompt = os.getenv("SYSTEM_PROMPT")
    # Note: create_agent uses 'system_prompt'
    agent = create_agent(llm_model, tools, system_prompt=system_prompt)

    # Inform the user they can start chatting
    console.print("[bold green]Connected to MCP servers. Start chatting! Type 'exit' to quit.[/bold green]")

    # Begin an infinite loop for interactive chat
    while True:
        # Get input from the user
        user_input = input(">>> ")

        # If user types "exit" or "quit", break out of the loop and stop the app
        if user_input.lower() in {"exit", "quit"}:
            break

        try:
            # Send the user's input to the agent for processing
            if detailed_output:
                # In detailed mode, we just await the full response
                response = await agent.ainvoke({"messages": user_input})
                console.print(f"[cyan]Agent (full):[/cyan] {response}")
            else:
                # Streaming Output
                console.print("[cyan]Agent:[/cyan] ", end="")
                async for event in agent.astream_events({"messages": user_input}, version="v2"):
                    if event["event"] == "on_chat_model_stream":
                        content = event["data"]["chunk"].content
                        if content:
                            console.print(content, end="")
                console.print() # Newline at the end
        except Exception as e:
            # If something goes wrong, print the error message
            console.print(f"[red]Error:[/red] {e}")

# === Run the async main() function using asyncio ===
if __name__ == "__main__":
    asyncio.run(main())

