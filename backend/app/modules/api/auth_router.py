from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import UserORM
from app.schemas.auth import (
    AuthResponse,
    BootstrapRequest,
    BootstrapStatusResponse,
    LoginRequest,
    UserResponse,
    UserRole,
)
from app.schemas.password_reset import (
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse,
    PasswordResetRequest as PasswordResetRequestSchema,
    PasswordResetRequestResponse,
)
from app.services.auth_service import (
    AuthService,
    BootstrapUnavailableError,
    InvalidCredentialsError,
)
from app.services.mail_delivery_service import MailDeliveryService
from app.services.password_reset_service import (
    GENERIC_REQUEST_MESSAGE,
    InvalidPasswordResetTokenError,
    PasswordResetService,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_response(user: UserORM) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=UserRole(user.role),
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.auth.session_cookie_name,
        value=token,
        max_age=settings.auth.session_ttl_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.auth.cookie_secure,
        samesite="lax",
        path="/",
    )


@router.get("/bootstrap-status", response_model=BootstrapStatusResponse)
def get_bootstrap_status(db: Session = Depends(get_db)) -> BootstrapStatusResponse:
    return BootstrapStatusResponse(bootstrap_required=AuthService(db).bootstrap_required())


@router.post("/bootstrap", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def bootstrap_administrator(
    request: BootstrapRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    service = AuthService(db)
    try:
        user = service.bootstrap_administrator(request)
    except BootstrapUnavailableError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    token, _ = service.create_session(user)
    _set_session_cookie(response, token)
    return AuthResponse(user=_user_response(user))


@router.post("/login", response_model=AuthResponse)
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    service = AuthService(db)
    try:
        user = service.authenticate(request)
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    token, _ = service.create_session(user)
    _set_session_cookie(response, token)
    return AuthResponse(user=_user_response(user))


def _deliver_password_reset_email(
    db: Session,
    *,
    recipient: str,
    reset_url: str,
) -> None:
    try:
        MailDeliveryService(db).send_password_reset_best_effort(
            recipient=recipient,
            reset_url=reset_url,
            expires_in_minutes=30,
        )
    except Exception:
        # Delivery failure must not change the generic public response.
        return


@router.post(
    "/password-reset/request",
    response_model=PasswordResetRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def request_password_reset(
    payload: PasswordResetRequestSchema,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> PasswordResetRequestResponse:
    client_ip = request.client.host if request.client is not None else "unknown"
    delivery = PasswordResetService(db).request_reset(payload, client_ip=client_ip)
    if delivery is not None:
        recipient, reset_url = delivery
        background_tasks.add_task(
            _deliver_password_reset_email,
            db,
            recipient=recipient,
            reset_url=reset_url,
        )
    return PasswordResetRequestResponse(message=GENERIC_REQUEST_MESSAGE)


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetConfirmResponse,
)
def confirm_password_reset(
    payload: PasswordResetConfirmRequest,
    db: Session = Depends(get_db),
) -> PasswordResetConfirmResponse:
    try:
        PasswordResetService(db).confirm_reset(
            raw_token=payload.token,
            password=payload.password,
        )
    except InvalidPasswordResetTokenError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return PasswordResetConfirmResponse(
        message="Пароль успешно изменён. Войдите с новым паролем."
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> None:
    AuthService(db).revoke_session(request.cookies.get(settings.auth.session_cookie_name))
    response.delete_cookie(
        key=settings.auth.session_cookie_name,
        path="/",
        secure=settings.auth.cookie_secure,
        httponly=True,
        samesite="lax",
    )


@router.get("/me", response_model=AuthResponse)
def get_me(user: UserORM = Depends(get_current_user)) -> AuthResponse:
    return AuthResponse(user=_user_response(user))
