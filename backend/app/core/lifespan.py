from contextlib import asynccontextmanager

from sqlalchemy import text

from app.core.database import engine
from app.models import DishORM, RecipeORM
from app.models.base import Base


@asynccontextmanager
async def lifespan(app):

    # register models
    _ = DishORM
    _ = RecipeORM

    # create tables
    Base.metadata.create_all(
        bind=engine
    )

    yield

    engine.dispose()