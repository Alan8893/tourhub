from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from sqlalchemy import select

from app.core.config import settings
from app.models.auth_session import AuthSessionORM
from app.models.password_reset import PasswordResetAttemptORM, PasswordResetTokenORM
from app.models.user import UserORM
from app.services.auth_service import hash_password, token_hash, utc_now
from app.services.mail_delivery_service import MailDeliveryService

GENERIC_MESSAGE = (
    "Если учётная запись с таким email существует, инструкция по восстановлению будет отправлена."
)


def _create_user(db_session, email: str = "member@example.org") -> UserORM:
    user = UserORM(
        email=email,
        display_name="Test Member",
        role="instructor",
        password_hash=hash_password("old-password-123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_request_reset_response_does_not_reveal_account_existence(
    auth_client, db_session, monkeypatch
) -> None:
    user = _create_user(db_session)
    monkeypatch.setattr(settings, "frontend_public_url", "https://tourhub.example.org")
    sent_urls: list[str] = []

    def fake_send(self, *, recipient: str, reset_url: str, expires_in_minutes: int):
        assert recipient == user.email
        assert expires_in_minutes == 30
        sent_urls.append(reset_url)

    monkeypatch.setattr(MailDeliveryService, "send_password_reset_best_effort", fake_send)

    unknown = auth_client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "unknown@example.org"},
    )
    existing = auth_client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": user.email},
    )

    assert unknown.status_code == existing.status_code == 202
    assert unknown.json() == existing.json() == {"message": GENERIC_MESSAGE}
    assert len(sent_urls) == 1
    token = parse_qs(urlparse(sent_urls[0]).fragment).get("token", [""])[0]
    assert token
    stored = db_session.scalar(
        select(PasswordResetTokenORM).where(PasswordResetTokenORM.user_id == user.id)
    )
    assert stored is not None
    assert stored.token_hash == token_hash(token)
    assert stored.token_hash != token
    assert token not in stored.token_hash


def test_confirm_reset_changes_password_and_revokes_sessions(
    auth_client, db_session
) -> None:
    user = _create_user(db_session)
    now = utc_now()
    raw_session = "opaque-session-token-for-test"
    session = AuthSessionORM(
        user_id=user.id,
        token_hash=token_hash(raw_session),
        expires_at=now + timedelta(days=1),
        last_seen_at=now,
    )
    raw_token = "reset-token-that-is-long-enough-for-tests"
    token = PasswordResetTokenORM(
        user_id=user.id,
        token_hash=token_hash(raw_token),
        expires_at=now + timedelta(minutes=30),
    )
    other_token = PasswordResetTokenORM(
        user_id=user.id,
        token_hash=token_hash("another-reset-token-that-is-long-enough"),
        expires_at=now + timedelta(minutes=30),
    )
    db_session.add_all([session, token, other_token])
    db_session.commit()

    response = auth_client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": raw_token, "password": "new-secure-password-123"},
    )

    assert response.status_code == 200
    db_session.refresh(user)
    db_session.refresh(session)
    db_session.refresh(token)
    db_session.refresh(other_token)
    assert user.password_hash != "new-secure-password-123"
    from app.services.auth_service import verify_password

    assert verify_password("new-secure-password-123", user.password_hash)
    assert session.revoked_at is not None
    assert token.consumed_at is not None
    assert other_token.consumed_at is not None


def test_expired_and_reused_reset_tokens_are_rejected(auth_client, db_session) -> None:
    user = _create_user(db_session)
    expired = PasswordResetTokenORM(
        user_id=user.id,
        token_hash=token_hash("expired-reset-token-that-is-long-enough"),
        expires_at=utc_now() - timedelta(seconds=1),
    )
    db_session.add(expired)
    db_session.commit()

    response = auth_client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "token": "expired-reset-token-that-is-long-enough",
            "password": "another-secure-password-123",
        },
    )
    assert response.status_code == 400

    valid_raw = "valid-reset-token-that-is-long-enough"
    valid = PasswordResetTokenORM(
        user_id=user.id,
        token_hash=token_hash(valid_raw),
        expires_at=utc_now() + timedelta(minutes=30),
    )
    db_session.add(valid)
    db_session.commit()
    first = auth_client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": valid_raw, "password": "another-secure-password-123"},
    )
    second = auth_client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": valid_raw, "password": "third-secure-password-123"},
    )
    assert first.status_code == 200
    assert second.status_code == 400


def test_smtp_failure_keeps_generic_request_response(
    auth_client, db_session, monkeypatch
) -> None:
    user = _create_user(db_session)
    monkeypatch.setattr(settings, "frontend_public_url", "https://tourhub.example.org")

    def fail_send(self, *, recipient: str, reset_url: str, expires_in_minutes: int):
        raise RuntimeError("SMTP internal failure")

    monkeypatch.setattr(MailDeliveryService, "send_password_reset_best_effort", fail_send)
    response = auth_client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": user.email},
    )

    assert response.status_code == 202
    assert response.json() == {"message": GENERIC_MESSAGE}
    assert "SMTP" not in response.text


def test_request_reset_is_throttled_persistently_per_email(
    auth_client, db_session, monkeypatch
) -> None:
    user = _create_user(db_session)
    monkeypatch.setattr(settings, "frontend_public_url", "https://tourhub.example.org")
    sent: list[str] = []

    def fake_send(self, *, recipient: str, reset_url: str, expires_in_minutes: int):
        sent.append(recipient)

    monkeypatch.setattr(MailDeliveryService, "send_password_reset_best_effort", fake_send)
    responses = [
        auth_client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": user.email},
        )
        for _ in range(4)
    ]

    assert all(response.status_code == 202 for response in responses)
    assert all(response.json() == {"message": GENERIC_MESSAGE} for response in responses)
    assert len(sent) == 3
    attempts = db_session.scalars(select(PasswordResetAttemptORM)).all()
    assert len(attempts) == 4
