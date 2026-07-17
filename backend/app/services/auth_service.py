import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.auth_session import AuthSessionORM
from app.models.identity_state import IdentityStateORM
from app.models.user import UserORM
from app.schemas.auth import BootstrapRequest, LoginRequest, UserRole

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_LENGTH = 64


class BootstrapUnavailableError(RuntimeError):
    pass


class InvalidCredentialsError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_LENGTH,
    )
    return "$".join(
        (
            "scrypt",
            str(_SCRYPT_N),
            str(_SCRYPT_R),
            str(_SCRYPT_P),
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(derived).decode("ascii"),
        )
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n_value, r_value, p_value, salt_value, digest_value = encoded.split("$")
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_value.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_value.encode("ascii"))
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n_value),
            r=int(r_value),
            p=int(p_value),
            dklen=len(expected),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _identity_state(self) -> IdentityStateORM:
        state = self.session.get(IdentityStateORM, 1)
        if state is not None:
            return state
        state = IdentityStateORM(id=1, bootstrap_completed=False, version=1)
        self.session.add(state)
        self.session.commit()
        self.session.refresh(state)
        return state

    def bootstrap_required(self) -> bool:
        state = self._identity_state()
        if state.bootstrap_completed:
            return False
        return self.session.scalar(select(UserORM.id).limit(1)) is None

    def bootstrap_administrator(self, request: BootstrapRequest) -> UserORM:
        self._identity_state()
        state = self.session.scalar(
            select(IdentityStateORM).where(IdentityStateORM.id == 1).with_for_update()
        )
        if state is None:
            raise RuntimeError("Identity state singleton is missing")
        existing_user = self.session.scalar(select(UserORM.id).limit(1))
        if state.bootstrap_completed or existing_user is not None:
            raise BootstrapUnavailableError("Первый администратор уже создан.")

        user = UserORM(
            email=request.email,
            display_name=request.display_name,
            role=UserRole.ADMINISTRATOR.value,
            password_hash=hash_password(request.password),
            is_active=True,
        )
        self.session.add(user)
        state.bootstrap_completed = True
        state.version += 1
        self.session.commit()
        self.session.refresh(user)
        return user

    def authenticate(self, request: LoginRequest) -> UserORM:
        user = self.session.scalar(select(UserORM).where(UserORM.email == request.email))
        valid = user is not None and user.is_active and verify_password(
            request.password, user.password_hash
        )
        if not valid or user is None:
            raise InvalidCredentialsError("Неверный email или пароль.")
        user.last_login_at = utc_now()
        self.session.commit()
        self.session.refresh(user)
        return user

    def create_session(self, user: UserORM) -> tuple[str, AuthSessionORM]:
        raw_token = secrets.token_urlsafe(32)
        now = utc_now()
        auth_session = AuthSessionORM(
            user_id=user.id,
            token_hash=token_hash(raw_token),
            expires_at=now + timedelta(days=settings.auth.session_ttl_days),
            last_seen_at=now,
        )
        self.session.add(auth_session)
        self.session.commit()
        self.session.refresh(auth_session)
        return raw_token, auth_session

    def resolve_user(self, raw_token: str) -> UserORM | None:
        now = utc_now()
        auth_session = self.session.scalar(
            select(AuthSessionORM)
            .options(joinedload(AuthSessionORM.user))
            .where(AuthSessionORM.token_hash == token_hash(raw_token))
        )
        if (
            auth_session is None
            or auth_session.revoked_at is not None
            or auth_session.expires_at <= now
            or not auth_session.user.is_active
        ):
            return None
        auth_session.last_seen_at = now
        self.session.commit()
        return auth_session.user

    def revoke_session(self, raw_token: str | None) -> None:
        if not raw_token:
            return
        auth_session = self.session.scalar(
            select(AuthSessionORM).where(AuthSessionORM.token_hash == token_hash(raw_token))
        )
        if auth_session is None or auth_session.revoked_at is not None:
            return
        auth_session.revoked_at = utc_now()
        self.session.commit()
