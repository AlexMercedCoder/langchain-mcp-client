# === Import standard and external libraries ===

import json  # Used for reading the MCP server config from a JSON file
import os  # Used for accessing environment variables
import asyncio  # Used for running asynchronous code
from dotenv import load_dotenv  # Loads environment variables from a `.env` file
from langchain_mcp_adapters.client import MultiServerMCPClient  # MCP client to connect to multiple servers
from langgraph.prebuilt import create_react_agent  # Helper to build a ReAct agent with LangChain and LangGraph
from rich.console import Console  # For pretty-printed CLI output

# Create a Rich console for styled terminal output
console = Console()

# Load environment variables from .env file (e.g., API keys, model name)
load_dotenv()

# Detailed Output Flag
detailed_output = os.getenv("DETAILED_OUTPUT", "false").lower() == "true"

# === Define the main asynchronous function ===
async def main():
    # Get environment variables for LLM API key and model
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm_model = os.getenv("LLM_MODEL")

    # If either variable is missing, inform the user and exit
    if not openai_api_key or not llm_model:
        console.print("[red]Missing OPENAI_API_KEY or LLM_MODEL in .env[/red]")
        return

    # Make sure the API key is available to LangChain tools (used internally by OpenAI integration)
    os.environ["OPENAI_API_KEY"] = openai_api_key

    # Load the list of MCP servers from a local JSON file
    with open("mcp_servers.json", "r") as f:
        server_config = json.load(f)

    # Create a MultiServer MCP client using the server definitions from the JSON
    client = MultiServerMCPClient(server_config)

    # Use the client to retrieve and load all available MCP tools
    tools = await client.get_tools()

    # Create a LangChain + LangGraph ReAct-style agent with the given model and tools
    agent = create_react_agent(llm_model, tools)

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
            response = await agent.ainvoke({"messages": user_input})

            # Print the response in styled CLI output
            if detailed_output:
                console.print(f"[cyan]Agent (full):[/cyan] {response}")
            else:
                # Extract just the last AIMessage content
                messages = response.get("messages", [])
                final_message = next((msg.content for msg in reversed(messages) if msg.type == "ai"), None)
                if final_message:
                    console.print(f"[cyan]Agent:[/cyan] {final_message}")
                else:
                    console.print("[yellow]No final AI response found.[/yellow]")
        except Exception as e:
            # If something goes wrong, print the error message
            console.print(f"[red]Error:[/red] {e}")

# === Run the async main() function using asyncio ===
if __name__ == "__main__":
    asyncio.run(main())

