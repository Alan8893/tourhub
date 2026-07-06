from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "TourHub",
        "environment": "development",
        "status": "running",
    }


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }