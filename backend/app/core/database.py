from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


# =========================
# Engine
# =========================

engine = create_engine(
    settings.database.url,
    pool_pre_ping=True,
    echo=False,
)


# =========================
# Session Factory
# =========================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# =========================
# Base (ORM foundation)
# =========================

class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    """
    pass


# =========================
# Dependency
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()