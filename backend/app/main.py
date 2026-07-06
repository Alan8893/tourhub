from fastapi import FastAPI

from app.core.lifespan import lifespan
from app.core.router import router

app = FastAPI(
    title="TourHub API",
    description="Backend API for TourHub.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)