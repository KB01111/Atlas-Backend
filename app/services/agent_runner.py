from app.db.crud.crud_agent import get_agent_by_id
from app.db.crud.crud_chat import get_messages, save_message
from app.services.litellm_service import call_litellm_completion
from app.services.gemini_service import gemini_generate_text
from app.services.a2a_service import send_a2a_task
from typing import Any

async def run_agent(user_id: str, agent_id: str, chat_session_id: str, user_message: str) -> Any:
    # Fetch agent config
    agent = await get_agent_by_id(agent_id, user_id)
    if not agent:
        raise Exception("Agent not found or not owned by user")
    provider = (agent.get("provider") or agent.get("framework") or "").lower()
    model = agent.get("model") or "gpt-4-turbo"
    plugin_config = agent.get("plugin_config") or {}

    # Fetch chat history (optional: limit for context window)
    history = await get_messages(chat_session_id, limit=20, offset=0)

    # Prepare messages/context for LLM
    messages = []
    if provider == "openai":
        # OpenAI expects a list of dicts with role/content
        messages = [{"role": m["sender_type"], "content": m["content"]} for m in history]
        messages.append({"role": "user", "content": user_message})
        response = await call_litellm_completion(user_id, "openai", model, messages)
        agent_reply = response["choices"][0]["message"]["content"]
    elif provider == "gemini":
        # Gemini expects a prompt string (can be improved for multi-turn)
        prompt = "\n".join([f'{m["sender_type"]}: {m["content"]}' for m in history])
        prompt += f"\nuser: {user_message}"
        agent_reply = await gemini_generate_text(user_id, prompt, model=model)
    elif provider == "a2a":
        # A2A expects a JSON-RPC call
        params = {
            "session_id": chat_session_id,
            "message": user_message,
            "history": history,
            "agent_id": agent_id
        }
        response = await send_a2a_task(user_id, agent.get("config", {}).get("a2a_url"), "tasks/send", params)
        agent_reply = response.get("result", {}).get("message", "")
    else:
        raise Exception(f"Unknown agent provider: {provider}")

    # Save agent's response as a message
    await save_message(chat_session_id, {
        "content": agent_reply,
        "sender_id": agent_id,
        "sender_type": "agent",
        "metadata": None
    })

    return {"response": agent_reply}