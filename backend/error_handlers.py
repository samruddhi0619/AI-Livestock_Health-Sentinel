import sys
import logging
from datetime import datetime, timezone
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("sentinel.errors")

def register_error_handlers(app):
    """
    Registers centralized, consistent error handlers for the FastAPI application.
    """
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        formatted_errors = []
        for err in exc.errors():
            loc = " -> ".join([str(l) for l in err.get("loc", [])])
            formatted_errors.append({
                "field": loc,
                "message": err.get("msg", ""),
                "type": err.get("type", "")
            })
            
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": "ValidationError",
                "message": "Input validation failed for request payload.",
                "details": formatted_errors,
                "status_code": 422,
                "path": str(request.url.path),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error on {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "DatabaseError",
                "message": "A database operation error occurred.",
                "status_code": 500,
                "path": str(request.url.path),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "InternalServerError",
                "message": "An unexpected internal server error occurred.",
                "status_code": 500,
                "path": str(request.url.path),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
