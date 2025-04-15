"""
Atlas AgentVerse Backend Entrypoint
- FastAPI app with modular routers
- Centralized error handling
- CORS, logging, and settings integration
- Ready for plugin, workflow, agent, chat, and LangGraph orchestration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Import routers (add more as you expand)
from app.api.endpoints import agents, chat, openai, plugin, realtime, workflow
from app.core import error_handlers
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Atlas AgentVerse Backend",
    version="0.1.0",
    description="API for managing agents, plugins, workflows, chat, and orchestration.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS.split(",")
    if settings.BACKEND_CORS_ORIGINS != "*"
    else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (modular, easy to expand)
app.include_router(plugin.router, prefix="/api/v1/plugins", tags=["plugins"])
app.include_router(workflow.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(realtime.router)
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(openai.router, prefix="/api/v1/openai", tags=["openai"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

# Ensure all exception handlers are registered
error_handlers.register_error_handlers(app)


# Startup/shutdown events for logging, DB, etc.
@app.on_event("startup")
def startup_event():
    logger.info("Atlas AgentVerse Backend starting up.")
    # Initialize DB, external services, etc. here


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Atlas AgentVerse Backend shutting down.")
    # Cleanup resources here


@app.get("/health")
async def health_check():
    return {"status": "ok"}
