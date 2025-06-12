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
    # Get LLM model from environment
    llm_model = os.getenv("LLM_MODEL")

    if not llm_model:
        console.print("[red]Missing LLM_MODEL in .env[/red]")
        return

    # Infer model provider from prefix
    provider_prefix = llm_model.split(":")[0]

    # Mapping of provider prefix to required env vars
    required_env_vars = {
        "openai": ["OPENAI_API_KEY"],
        "anthropic": ["ANTHROPIC_API_KEY"],
        "google": ["GOOGLE_API_KEY"],
        "mistral": ["MISTRAL_API_KEY"],
        "cohere": ["COHERE_API_KEY"],
        "together": ["TOGETHER_API_KEY"],
        "fireworks": ["FIREWORKS_API_KEY"],
        "azure": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"],
        "bedrock": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]
    }

    # Check if the provider is supported
    if provider_prefix not in required_env_vars:
        console.print(f"[red]Unsupported LLM provider prefix: '{provider_prefix}'[/red]")
        return

    # Validate that all required environment variables are present
    missing_vars = [var for var in required_env_vars[provider_prefix] if not os.getenv(var)]
    if missing_vars:
        console.print(f"[red]Missing required environment variables for {provider_prefix}: {', '.join(missing_vars)}[/red]")
        return

    # Optionally set them into os.environ (if using libraries that expect them there)
    for var in required_env_vars[provider_prefix]:
        os.environ[var] = os.getenv(var)

    console.print(f"[green]Using model:[/green] {llm_model}")

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

