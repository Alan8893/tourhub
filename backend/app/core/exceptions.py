import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


log = structlog.get_logger()


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    log.error(
        "http_exception",
        path=request.url.path,
        status_code=exc.status_code,
        detail=str(exc.detail),
        request_id=getattr(request.state, "request_id", None),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log.error(
        "validation_error",
        path=request.url.path,
        errors=exc.errors(),
        request_id=getattr(request.state, "request_id", None),
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": exc.errors(),
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    log.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        request_id=getattr(request.state, "request_id", None),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "request_id": getattr(request.state, "request_id", None),
        },
    )