from contextlib import asynccontextmanager

from app.core.database import engine


@asynccontextmanager
async def lifespan(app):

    yield

    engine.dispose()