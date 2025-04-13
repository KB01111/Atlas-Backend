import litellm
from app.services.key_service import get_api_key

async def call_litellm_completion(user_id: str, service: str, model: str, messages: list, options: dict = None):
    api_key = await get_api_key(user_id, service)
    if not api_key:
        raise Exception(f"No API key found for service: {service}")
    # Set the API key for the provider dynamically
    # For OpenAI: litellm.openai_api_key, for others: see LiteLLM docs
    if service.lower() == "openai":
        litellm.openai_api_key = api_key
        # Optionally handle OpenAI Assistants API or v2 here in the future
    elif service.lower() == "azure":
        litellm.azure_api_key = api_key
    elif service.lower() == "anthropic":
        litellm.anthropic_api_key = api_key
    # Add more providers as needed

    completion = await litellm.acompletion(
        model=model,
        messages=messages,
        **(options or {})
    )
    return completion