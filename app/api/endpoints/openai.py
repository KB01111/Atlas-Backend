from typing import Any, List, Optional

import openai
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(prefix="/openai", tags=["openai"])

class AssistantCreateRequest(BaseModel):
    name: str
    instructions: Optional[str] = None
    tools: Optional[List[Any]] = None
    model: Optional[str] = "gpt-4-turbo"

@router.post("/assistant")
async def create_assistant(req: AssistantCreateRequest):
    try:
        openai.api_key = get_settings().OPENAI_API_KEY
        assistant = openai.beta.assistants.create(
            name=req.name,
            instructions=req.instructions,
            tools=req.tools,
            model=req.model,
        )
        return {"assistant": assistant}
    except Exception as e:
        return {"error": str(e)}

@router.get("/assistant")
async def list_assistants():
    try:
        openai.api_key = get_settings().OPENAI_API_KEY
        assistants = openai.beta.assistants.list()
        return {"assistants": assistants}
    except Exception as e:
        return {"error": str(e)}

class ThreadCreateRequest(BaseModel):
    pass

@router.post("/thread")
async def create_thread(req: ThreadCreateRequest):
    try:
        openai.api_key = get_settings().OPENAI_API_KEY
        thread = openai.beta.threads.create()
        return {"thread": thread}
    except Exception as e:
        return {"error": str(e)}

@router.get("/thread")
async def list_threads():
    try:
        openai.api_key = get_settings().OPENAI_API_KEY
        threads = openai.beta.threads.list()
        return {"threads": threads}
    except Exception as e:
        return {"error": str(e)}

class MessageCreateRequest(BaseModel):
    thread_id: str
    role: str
    content: str

@router.post("/message")
async def add_message(req: MessageCreateRequest):
    try:
        openai.api_key = get_settings().OPENAI_API_KEY
        message = openai.beta.threads.messages.create(
            thread_id=req.thread_id,
            role=req.role,
            content=req.content,
        )
        return {"message": message}
    except Exception as e:
        return {"error": str(e)}

class RunAssistantRequest(BaseModel):
    assistant_id: str
    thread_id: str

@router.post("/run")
async def run_assistant(req: RunAssistantRequest):
    try:
        openai.api_key = get_settings().OPENAI_API_KEY
        run = openai.beta.threads.runs.create(
            thread_id=req.thread_id,
            assistant_id=req.assistant_id,
        )
        return {"run": run}
    except Exception as e:
        return {"error": str(e)}
