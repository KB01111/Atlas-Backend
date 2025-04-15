from agents import Agent, Runner
from pydantic import BaseModel

from app.db.crud.crud_agent import get_agent_by_id
from app.db.crud.crud_chat import get_messages, save_message
from app.models.agent import AgentOut
from app.services.a2a_service import send_a2a_task
from app.services.gemini_service import gemini_generate_text


class AgentResponse(BaseModel):
    response: str
    agent: AgentOut

async def run_agent(user_id: str, agent_id: str, chat_session_id: str, user_message: str) -> AgentResponse:
    # Fetch agent config
    agent = await get_agent_by_id(agent_id, user_id)
    if not agent:
        raise Exception("Agent not found or not owned by user")
    provider = (agent.get("provider") or agent.get("framework") or "").lower()
    model = agent.get("model") or "gpt-4-turbo"
    agent.get("plugin_config") or {}

    # Fetch chat history (optional: limit for context window)
    history = await get_messages(chat_session_id, limit=20, offset=0)

    # Prepare messages/context for LLM
    if provider == "openai-agent-sdk":
        # Use OpenAI Agents SDK for orchestration
        instructions = agent.get("instructions") or "You are a helpful assistant."
        openai_agent = Agent(name=agent.get("name", "Assistant"), instructions=instructions)
        # Compose the prompt from user message and history (simple concat for demo)
        prompt = user_message
        if history:
            prompt = "\n".join([msg["content"] for msg in history if msg["role"] == "user"]) + f"\n{user_message}"
        # Run agent using SDK (sync wrapper for demo; production: use async)
        result = await Runner.run_async(openai_agent, prompt)
        agent_reply = result.final_output
    elif provider == "litellm":
        # Use LiteLLM for any supported model/provider
        from app.services.litellm_service import call_litellm_completion
        service = agent.get("litellm_service") or agent.get("provider") or "openai"
        model = agent.get("model") or "gpt-4-turbo"
        options = agent.get("litellm_options") or {}
        response = await call_litellm_completion(
            user_id,
            service,
            model,
            history + [{"role": "user", "content": user_message}],
            options
        )
        agent_reply = response["choices"][0]["message"]["content"]
    elif provider == "openai":
        response = await call_litellm_completion(user_id, provider, model, history + [{"role": "user", "content": user_message}])
        agent_reply = response["choices"][0]["message"]["content"]
    elif provider == "gemini":
        agent_reply = await gemini_generate_text(user_id, user_message, model)
    elif provider == "a2a":
        params = {
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

    return AgentResponse(response=agent_reply, agent=AgentOut(**agent))
