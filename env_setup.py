import os
from rich.console import Console

console = Console()

def setup_llm_environment():
    llm_model = os.getenv("LLM_MODEL")

    if not llm_model:
        raise ValueError("Missing LLM_MODEL in .env")

    provider_prefix = llm_model.split(":")[0]

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

    if provider_prefix not in required_env_vars:
        raise ValueError(f"Unsupported LLM provider prefix: {provider_prefix}")

    missing = [var for var in required_env_vars[provider_prefix] if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required env vars for {provider_prefix}: {', '.join(missing)}")

    # Inject into os.environ for downstream compatibility
    for var in required_env_vars[provider_prefix]:
        os.environ[var] = os.getenv(var)

    return llm_model
