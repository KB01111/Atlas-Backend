from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.core.security import get_current_user_id
from app.services.litellm_service import (
    call_litellm_completion,
    call_litellm_embedding,
    call_litellm_image_generation,
    call_litellm_stream,
    list_litellm_models,
    litellm_router,
)

router = APIRouter(prefix="/litellm", tags=["litellm"])


class LitellmChatRequest(BaseModel):
    service: str
    model: str
    messages: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None


class LitellmEmbeddingRequest(BaseModel):
    service: str
    model: str
    input: list
    options: Optional[Dict[str, Any]] = None


class LitellmImageRequest(BaseModel):
    service: str
    model: str
    prompt: str
    options: Optional[Dict[str, Any]] = None


@router.post("/chat")
async def litellm_chat(
    req: LitellmChatRequest, user_id: str = Depends(get_current_user_id)
):
    try:
        response = await call_litellm_completion(
            user_id=user_id,
            service=req.service,
            model=req.model,
            messages=req.messages,
            options=req.options,
        )
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}


@router.post("/embedding")
async def litellm_embedding(
    req: LitellmEmbeddingRequest, user_id: str = Depends(get_current_user_id)
):
    try:
        response = await call_litellm_embedding(
            user_id=user_id,
            service=req.service,
            model=req.model,
            input=req.input,
            options=req.options,
        )
        return {"embedding": response}
    except Exception as e:
        return {"error": str(e)}


@router.post("/image")
async def litellm_image(
    req: LitellmImageRequest, user_id: str = Depends(get_current_user_id)
):
    try:
        response = await call_litellm_image_generation(
            user_id=user_id,
            service=req.service,
            model=req.model,
            prompt=req.prompt,
            options=req.options,
        )
        return {"image": response}
    except Exception as e:
        return {"error": str(e)}


@router.post("/stream")
async def litellm_stream(
    req: LitellmChatRequest, user_id: str = Depends(get_current_user_id)
):
    async def event_stream():
        async for chunk in call_litellm_stream(
            user_id=user_id,
            service=req.service,
            model=req.model,
            messages=req.messages,
            options=req.options,
        ):
            yield (
                chunk["choices"][0]["delta"]["content"]
                if "choices" in chunk and chunk["choices"][0].get("delta")
                else ""
            )

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/models")
async def litellm_models():
    return {"models": list_litellm_models()}


@router.post("/router")
async def litellm_router_endpoint(
    request: Request,
):
    body = await request.json()
    try:
        result = litellm_router(
            user_id=body.get("user_id", ""),
            router_config=body.get("router_config", {}),
            messages=body.get("messages", []),
            options=body.get("options", {}),
        )
        return {"result": result}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Optional: OpenAI-compatible proxy endpoint
@router.api_route("/v1/chat/completions", methods=["POST"])
async def openai_proxy(request: Request):
    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:4000/v1/chat/completions",
            content=await request.body(),
            headers=request.headers,
        )
        return JSONResponse(resp.json(), status_code=resp.status_code)
