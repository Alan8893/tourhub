from fastapi import FastAPI

from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.router import router


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.include_router(router)