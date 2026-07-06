from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["System"])
async def root() -> dict[str, str]:
    """
    Root endpoint.
    """
    return {
        "status": "ok",
        "project": "TourHub",
    }


@router.get("/health", tags=["System"])
async def health() -> dict[str, str]:
    """
    Healthcheck endpoint.
    """
    return {
        "status": "healthy",
    }