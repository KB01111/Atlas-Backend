import sqlalchemy.exc
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.endpoints.agents import router as agents_router
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.litellm import router as litellm_router
from app.api.endpoints.openai import router as openai_router
from app.api.endpoints.plugin import router as plugin_router
from app.api.endpoints.workflow import router as workflow_router
from app.core.config import settings
from app.core.error_handlers import (
    db_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    supabase_exception_handler,
    validation_exception_handler,
)
from app.db.supabase_client import SupabaseClientError

app = FastAPI()

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(sqlalchemy.exc.SQLAlchemyError, db_exception_handler)
app.add_exception_handler(SupabaseClientError, supabase_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.BACKEND_CORS_ORIGINS] if settings.BACKEND_CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logger.add("backend.log", rotation="1 week")

# Mount routers
app.include_router(openai_router, prefix="/api/v1")
app.include_router(litellm_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(plugin_router, prefix="/api/v1")
app.include_router(workflow_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Agent Backend running"}
