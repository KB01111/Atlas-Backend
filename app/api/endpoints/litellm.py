from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import litellm
from app.core.config import settings

router = APIRouter(prefix="/litellm", tags=["litellm"])

from fastapi import Depends
from app.core.security import get_current_user_id
from app.services.litellm_service import call_litellm_completion

class LitellmChatRequest(BaseModel):
    service: str
    model: str
    messages: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None

@router.post("/chat")
async def litellm_chat(
    req: LitellmChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    try:
        response = await call_litellm_completion(
            user_id=user_id,
            service=req.service,
            model=req.model,
            messages=req.messages,
            options=req.options
        )
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}