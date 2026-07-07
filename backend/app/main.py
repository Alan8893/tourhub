from fastapi import FastAPI

from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.router import router
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


setup_logging()

app = FastAPI(
    title=settings.app_name,
    description="TourHub ERP API for hiking preparation workflow.",
    version="0.1.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestContextMiddleware)

# Routers
app.include_router(router)

# Exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
