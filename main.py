from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.api.endpoints.openai import router as openai_router
from app.api.endpoints.litellm import router as litellm_router
from app.api.endpoints.agents import router as agents_router

app = FastAPI()
from app.api.endpoints.chat import router as chat_router

# Exception Handlers
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
import sqlalchemy.exc
from app.core.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    db_exception_handler,
    generic_exception_handler,
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(sqlalchemy.exc.SQLAlchemyError, db_exception_handler)
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

@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Agent Backend running"}
