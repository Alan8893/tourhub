import pytest

from app.schemas.mail_settings import MailDeliveryStatus
from app.services import mail_delivery_service as delivery_module
from app.services.mail_delivery_service import (
    MailDeliveryService,
    MailDeliveryUnavailableError,
)
from app.services.mail_settings_service import MailSettingsService


class FakeSMTP:
    instances: list["FakeSMTP"] = []
    failures_remaining = 0
    implicit_tls = False

    def __init__(self, host: str, port: int, **kwargs: object) -> None:
        if type(self).failures_remaining:
            type(self).failures_remaining -= 1
            raise OSError("temporary fake failure")
        self.host = host
        self.port = port
        self.kwargs = kwargs
        self.started_tls = False
        self.login_args: tuple[str, str] | None = None
        self.messages: list[object] = []
        self.noop_calls = 0
        type(self).instances.append(self)

    def ehlo_or_helo_if_needed(self) -> None:
        return None

    def starttls(self, **_: object) -> tuple[int, bytes]:
        self.started_tls = True
        return 220, b"ready"

    def ehlo(self) -> tuple[int, bytes]:
        return 250, b"ok"

    def login(self, username: str, secret: str) -> tuple[int, bytes]:
        self.login_args = (username, secret)
        return 235, b"ok"

    def send_message(self, message: object) -> dict[str, object]:
        self.messages.append(message)
        return {}

    def noop(self) -> tuple[int, bytes]:
        self.noop_calls += 1
        return 250, b"ok"

    def quit(self) -> tuple[int, bytes]:
        return 221, b"bye"

    def close(self) -> None:
        return None


class FakeSMTPSSL(FakeSMTP):
    implicit_tls = True


@pytest.fixture(autouse=True)
def reset_fake_smtp(monkeypatch):
    FakeSMTP.instances = []
    FakeSMTP.failures_remaining = 0
    FakeSMTPSSL.instances = []
    FakeSMTPSSL.failures_remaining = 0
    monkeypatch.setattr(delivery_module.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(delivery_module.smtplib, "SMTP_SSL", FakeSMTPSSL)


@pytest.mark.parametrize(
    ("mode", "client_type", "starts_tls"),
    [
        ("plain", FakeSMTP, False),
        ("starttls", FakeSMTP, True),
        ("tls", FakeSMTPSSL, False),
    ],
)
def test_test_message_supports_all_connection_modes(
    db_session,
    monkeypatch,
    mode: str,
    client_type: type[FakeSMTP],
    starts_tls: bool,
) -> None:
    marker = "environment-only-test-value"
    monkeypatch.setenv("TOURHUB_SMTP_SECRET", marker)
    settings = MailSettingsService(db_session).get()
    settings.smtp_host = "smtp.example.org"
    settings.smtp_port = 2525
    settings.security_mode = mode
    settings.smtp_username = "mailer"
    settings.sender_email = "tourhub@example.org"
    settings.sender_name = "TourHub Club"
    settings.reply_to_email = "reply@example.org"
    settings.test_recipient_email = "admin@example.org"
    settings.retry_count = 0
    db_session.commit()

    result = MailDeliveryService(db_session, sleeper=lambda _: None).send_test_message()

    assert result.status is MailDeliveryStatus.SENT
    assert result.recipient == "admin@example.org"
    assert result.attempts == 1
    client = client_type.instances[-1]
    assert client.host == "smtp.example.org"
    assert client.port == 2525
    assert client.started_tls is starts_tls
    assert client.login_args == ("mailer", marker)
    message = client.messages[0]
    assert message["Subject"] == "Проверка почты TourHub"
    assert message["To"] == "admin@example.org"
    assert message["Reply-To"] == "reply@example.org"
    assert marker not in message.as_string()


def test_connection_check_retries_and_does_not_send(db_session) -> None:
    settings = MailSettingsService(db_session).get()
    settings.security_mode = "plain"
    settings.smtp_username = None
    settings.retry_count = 1
    db_session.commit()
    FakeSMTP.failures_remaining = 1

    result = MailDeliveryService(db_session, sleeper=lambda _: None).check_connection()

    assert result.status is MailDeliveryStatus.SENT
    assert result.attempts == 2
    client = FakeSMTP.instances[-1]
    assert client.noop_calls == 1
    assert client.messages == []


def test_username_requires_environment_value(db_session, monkeypatch) -> None:
    monkeypatch.delenv("TOURHUB_SMTP_SECRET", raising=False)
    settings = MailSettingsService(db_session).get()
    settings.smtp_username = "mailer"
    settings.retry_count = 0
    db_session.commit()

    with pytest.raises(MailDeliveryUnavailableError):
        MailDeliveryService(db_session, sleeper=lambda _: None).check_connection()
    assert FakeSMTP.instances == []


def test_invitation_failure_keeps_safe_manual_fallback(db_session) -> None:
    settings = MailSettingsService(db_session).get()
    settings.security_mode = "plain"
    settings.smtp_username = None
    settings.retry_count = 1
    db_session.commit()
    FakeSMTP.failures_remaining = 2

    result = MailDeliveryService(db_session, sleeper=lambda _: None).send_invitation_best_effort(
        recipient="member@example.org",
        role_label="Инструктор",
        expires_at=settings.updated_at,
        acceptance_url="http://tourhub.local/accept-invitation#token=example",
    )

    assert result.status is MailDeliveryStatus.FAILED
    assert result.attempts == 2
    assert "Передайте ссылку вручную" in result.message
    assert "example" not in result.message
