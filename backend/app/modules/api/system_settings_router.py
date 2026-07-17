from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.club_settings import ClubSettingsORM
from app.schemas.club_settings import (
    ClubImagesResponse,
    ClubSettingsDetailResponse,
    ClubSettingsDetailUpdateRequest,
    ClubSocialLink,
    SystemSettingsHistoryResponse,
)
from app.services.club_settings_service import (
    ClubImageKind,
    ClubSettingsService,
    SettingsVersionConflictError,
)

router = APIRouter(prefix="/settings", tags=["settings"])


def _club_response(
    service: ClubSettingsService,
    settings: ClubSettingsORM,
) -> ClubSettingsDetailResponse:
    return ClubSettingsDetailResponse(
        version=settings.version,
        club_name=settings.club_name,
        short_name=settings.short_name,
        legal_name=settings.legal_name,
        description=settings.description,
        address=settings.address,
        phone=settings.phone,
        email=settings.email,
        website=settings.website,
        timezone=settings.timezone,
        city=settings.city,
        region=settings.region,
        social_links=[ClubSocialLink(**link) for link in settings.social_links],
        images=ClubImagesResponse(
            main_logo_data_url=service.image_data_url(
                settings,
                ClubImageKind.MAIN_LOGO,
            ),
            light_logo_data_url=service.image_data_url(
                settings,
                ClubImageKind.LIGHT_LOGO,
            ),
            dark_logo_data_url=service.image_data_url(
                settings,
                ClubImageKind.DARK_LOGO,
            ),
            square_icon_data_url=service.image_data_url(
                settings,
                ClubImageKind.SQUARE_ICON,
            ),
            favicon_data_url=service.image_data_url(
                settings,
                ClubImageKind.FAVICON,
            ),
            login_background_data_url=service.image_data_url(
                settings,
                ClubImageKind.LOGIN_BACKGROUND,
            ),
            document_image_data_url=service.image_data_url(
                settings,
                ClubImageKind.DOCUMENT_IMAGE,
            ),
        ),
        updated_at=settings.updated_at,
    )


@router.get("/club", response_model=ClubSettingsDetailResponse)
def get_club_settings(
    db: Session = Depends(get_db),
) -> ClubSettingsDetailResponse:
    service = ClubSettingsService(db)
    return _club_response(service, service.get())


@router.put("/club", response_model=ClubSettingsDetailResponse)
def update_club_settings(
    request: ClubSettingsDetailUpdateRequest,
    db: Session = Depends(get_db),
) -> ClubSettingsDetailResponse:
    service = ClubSettingsService(db)
    try:
        # Serialize version checks and writes on PostgreSQL. The selected ORM row is
        # reused by the service through the session identity map, so a concurrent
        # request observes the committed version before it may update the singleton.
        db.scalar(
            select(ClubSettingsORM)
            .where(ClubSettingsORM.id == 1)
            .with_for_update()
        )
        settings = service.update_details(request)
    except SettingsVersionConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _club_response(service, settings)


@router.get("/history", response_model=list[SystemSettingsHistoryResponse])
def get_settings_history(
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[SystemSettingsHistoryResponse]:
    history = ClubSettingsService(db).list_history(limit=limit)
    return [
        SystemSettingsHistoryResponse(
            id=item.id,
            section=item.section,
            actor_label=item.actor_label,
            action=item.action,
            changed_fields=item.changed_fields,
            settings_version=item.settings_version,
            created_at=item.created_at,
        )
        for item in history
    ]
