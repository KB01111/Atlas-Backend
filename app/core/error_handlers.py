import sqlalchemy.exc
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.db.supabase_client import SupabaseClientError


def format_error_response(status_code: int, detail: str, error_type: str = "error"):
    """Format a standard error response dictionary."""
    return {"status": "error", "error_type": error_type, "detail": detail}


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTPExceptions."""
    logger.error(f"HTTPException: {exc.detail} | Path: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(exc.status_code, exc.detail, "http_exception"),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic RequestValidationErrors."""
    logger.error(f"Validation error: {exc.errors()} | Path: {request.url}")
    return JSONResponse(
        status_code=422,
        content=format_error_response(422, str(exc.errors()), "validation_error"),
    )


async def db_exception_handler(request: Request, exc: sqlalchemy.exc.SQLAlchemyError):
    """Handle generic SQLAlchemy database errors."""
    logger.error(f"Database error: {exc!s} | Path: {request.url}")
    return JSONResponse(
        status_code=500,
        content=format_error_response(
            500, "A database error occurred.", "database_error"
        ),
    )


async def supabase_exception_handler(request: Request, exc: SupabaseClientError):
    """Handle custom Supabase client errors."""
    logger.error(f"Supabase error: {exc!s} | Path: {request.url}")
    return JSONResponse(
        status_code=500,
        content=format_error_response(500, str(exc), "supabase_error"),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle any other unhandled exceptions."""
    logger.error(
        f"Unhandled exception: {exc!s} | Path: {request.url}", exc_info=True
    )  # Include stack trace in logs
    return JSONResponse(
        status_code=500,
        content=format_error_response(
            500,
            "An internal server error occurred. Please check the logs.",
            "internal_error",
        ),  # More informative message
    )


def register_error_handlers(app):
    """Register all custom exception handlers with the FastAPI app."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(sqlalchemy.exc.SQLAlchemyError, db_exception_handler)
    app.add_exception_handler(SupabaseClientError, supabase_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
