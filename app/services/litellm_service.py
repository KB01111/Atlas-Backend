import litellm

from app.services.key_service import get_api_key


async def call_litellm_completion(
    user_id: str, service: str, model: str, messages: list, options: dict = None
):
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
        model=model, messages=messages, **(options or {})
    )
    return completion


async def call_litellm_embedding(
    user_id: str, service: str, model: str, input: list, options: dict = None
):
    api_key = await get_api_key(user_id, service)
    if not api_key:
        raise Exception(f"No API key found for service: {service}")
    if service.lower() == "openai":
        litellm.openai_api_key = api_key
    elif service.lower() == "azure":
        litellm.azure_api_key = api_key
    elif service.lower() == "anthropic":
        litellm.anthropic_api_key = api_key
    # Add more providers as needed
    embedding = await litellm.aembedding(model=model, input=input, **(options or {}))
    return embedding


async def call_litellm_image_generation(
    user_id: str, service: str, model: str, prompt: str, options: dict = None
):
    api_key = await get_api_key(user_id, service)
    if not api_key:
        raise Exception(f"No API key found for service: {service}")
    if service.lower() == "openai":
        litellm.openai_api_key = api_key
    elif service.lower() == "azure":
        litellm.azure_api_key = api_key
    elif service.lower() == "anthropic":
        litellm.anthropic_api_key = api_key
    # Add more providers as needed
    image = await litellm.aimage_generation(
        model=model, prompt=prompt, **(options or {})
    )
    return image


async def call_litellm_stream(
    user_id: str, service: str, model: str, messages: list, options: dict = None
):
    api_key = await get_api_key(user_id, service)
    if not api_key:
        raise Exception(f"No API key found for service: {service}")
    if service.lower() == "openai":
        litellm.openai_api_key = api_key
    elif service.lower() == "azure":
        litellm.azure_api_key = api_key
    elif service.lower() == "anthropic":
        litellm.anthropic_api_key = api_key
    # Add more providers as needed
    async for chunk in litellm.acompletion(
        model=model, messages=messages, stream=True, **(options or {})
    ):
        yield chunk


# Model listing for demo (could be static or from config)
def list_litellm_models():
    # In production, this should be dynamic or from config
    return [
        {"provider": "openai", "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]},
        {"provider": "anthropic", "models": ["claude-3-opus", "claude-3-sonnet"]},
        {"provider": "ollama", "models": ["llama2", "mistral"]},
    ]


# Router/failover: wrapper for router logic
def litellm_router(
    user_id: str, router_config: dict, messages: list, options: dict = None
):
    # router_config example: {"providers": ["openai", "anthropic"], "fallback": True}
    # This is a simple demo; real logic could use litellm's router/fallback features
    for provider in router_config.get("providers", []):
        try:
            # Could use call_litellm_completion with provider
            # For demo, call synchronously (should be async in real usage)
            # This is a placeholder for actual router logic
            return provider  # Replace with actual call
        except Exception:
            continue
    raise Exception("All providers failed")
