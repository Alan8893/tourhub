from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import (
    alcohol_policy_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.lifespan import lifespan
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.core.router import router
from app.policies.alcohol_policy import AlcoholPolicyViolation

setup_logging()

app = FastAPI(
    title=settings.app_name,
    description="TourHub ERP API for hiking preparation workflow.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)

app.include_router(router)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AlcoholPolicyViolation, alcohol_policy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
