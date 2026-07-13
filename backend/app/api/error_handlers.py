from __future__ import annotations

import traceback
from typing import Any

import loguru
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.services.errors import AppError


def _error_response(
    status_code: int,
    message: str,
    detail: Any = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "error": {
            "code": status_code,
            "message": message,
        }
    }
    if detail is not None:
        body["error"]["detail"] = detail
    return JSONResponse(status_code=status_code, content=body)


def register_error_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""

    @app.exception_handler(AppError)
    async def app_error_handler(
        request: Request, exc: AppError
    ) -> JSONResponse:
        loguru.logger.warning(
            "Application error: {} {} -> {} {}",
            request.method,
            request.url.path,
            exc.status_code,
            exc.message,
        )
        return _error_response(
            status_code=exc.status_code,
            message=exc.message,
            detail=exc.detail,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        loguru.logger.warning(
            "Validation error: {} {} -> {}",
            request.method,
            request.url.path,
            exc.errors(),
        )
        return _error_response(
            status_code=422,
            message="Request validation failed",
            detail=exc.errors(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        loguru.logger.warning(
            "HTTP error: {} {} -> {} {}",
            request.method,
            request.url.path,
            exc.status_code,
            exc.detail,
        )
        return _error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        loguru.logger.error(
            "Unhandled error: {} {}\n{}",
            request.method,
            request.url.path,
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        )
        return _error_response(
            status_code=500,
            message="Internal server error",
        )
