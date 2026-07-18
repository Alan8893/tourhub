from __future__ import annotations

import os
import smtplib
import ssl
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr
from typing import Iterator

from sqlalchemy.orm import Session

from app.models.mail_settings import MailSettingsORM
from app.schemas.mail_settings import MailDeliveryStatus
from app.services.mail_settings_service import MAIL_SECRET_ENV_VAR, MailSettingsService


class MailDeliveryUnavailableError(RuntimeError):
    pass


class MailDeliveryFailedError(RuntimeError):
    def __init__(self, message: str, *, attempts: int) -> None:
        super().__init__(message)
        self.attempts = attempts


@dataclass(frozen=True)
class MailDeliveryResult:
    status: MailDeliveryStatus
    message: str
    attempts: int
    recipient: str | None = None


class MailDeliveryService:
    def __init__(
        self,
        session: Session,
        *,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.session = session
        self.sleeper = sleeper

    @staticmethod
    def configuration_available(settings: MailSettingsORM) -> bool:
        if not settings.smtp_username:
            return True
        value = os.getenv(MAIL_SECRET_ENV_VAR)
        return bool(value and value.strip())

    @classmethod
    def test_delivery_available(cls, settings: MailSettingsORM) -> bool:
        return cls.configuration_available(settings) and bool(settings.test_recipient_email)

    def check_connection(self) -> MailDeliveryResult:
        settings = MailSettingsService(self.session).get()
        attempts = self._run_with_retries(settings, self._check_once)
        return MailDeliveryResult(
            status=MailDeliveryStatus.SENT,
            message="Соединение с SMTP-сервером установлено и проверено.",
            attempts=attempts,
        )

    def send_test_message(self) -> MailDeliveryResult:
        settings = MailSettingsService(self.session).get()
        recipient = settings.test_recipient_email
        if not recipient:
            raise MailDeliveryUnavailableError(
                "Укажите и сохраните тестовый адрес получателя."
            )
        message = self._message(
            settings,
            recipient=recipient,
            subject="Проверка почты TourHub",
            body=(
                "Это тестовое письмо TourHub.\n\n"
                "SMTP-подключение работает, а сохранённые параметры отправителя применены.\n"
                "Никаких действий выполнять не требуется."
            ),
        )
        attempts = self._run_with_retries(
            settings,
            lambda client: client.send_message(message),
        )
        return MailDeliveryResult(
            status=MailDeliveryStatus.SENT,
            message="Тестовое письмо отправлено.",
            attempts=attempts,
            recipient=recipient,
        )

    def send_invitation_best_effort(
        self,
        *,
        recipient: str,
        role_label: str,
        expires_at: datetime,
        acceptance_url: str,
    ) -> MailDeliveryResult:
        settings = MailSettingsService(self.session).get()
        if not self.configuration_available(settings):
            return MailDeliveryResult(
                status=MailDeliveryStatus.UNAVAILABLE,
                message=(
                    "Автоматическая отправка недоступна: для SMTP username не настроено "
                    f"значение {MAIL_SECRET_ENV_VAR}."
                ),
                attempts=0,
                recipient=recipient,
            )
        message = self._message(
            settings,
            recipient=recipient,
            subject="Приглашение в TourHub",
            body=(
                "Вас пригласили в TourHub.\n\n"
                f"Роль: {role_label}.\n"
                f"Ссылка действует до: {expires_at:%d.%m.%Y %H:%M}.\n\n"
                f"Откройте ссылку для создания учётной записи:\n{acceptance_url}\n\n"
                "Если вы не ожидали это приглашение, проигнорируйте письмо."
            ),
        )
        try:
            attempts = self._run_with_retries(
                settings,
                lambda client: client.send_message(message),
            )
        except MailDeliveryUnavailableError as error:
            return MailDeliveryResult(
                status=MailDeliveryStatus.UNAVAILABLE,
                message=str(error),
                attempts=0,
                recipient=recipient,
            )
        except MailDeliveryFailedError as error:
            return MailDeliveryResult(
                status=MailDeliveryStatus.FAILED,
                message=(
                    "Приглашение создано, но SMTP-доставка не удалась. "
                    "Передайте ссылку вручную или повторите выпуск позже."
                ),
                attempts=error.attempts,
                recipient=recipient,
            )
        return MailDeliveryResult(
            status=MailDeliveryStatus.SENT,
            message="Приглашение отправлено по email; ручная ссылка также доступна.",
            attempts=attempts,
            recipient=recipient,
        )

    def _run_with_retries(
        self,
        settings: MailSettingsORM,
        operation: Callable[[smtplib.SMTP], object],
    ) -> int:
        if not self.configuration_available(settings):
            raise MailDeliveryUnavailableError(
                f"Для SMTP username требуется значение {MAIL_SECRET_ENV_VAR}."
            )
        total_attempts = settings.retry_count + 1
        last_error: Exception | None = None
        for attempt in range(1, total_attempts + 1):
            try:
                with self._connection(settings) as client:
                    operation(client)
                return attempt
            except (OSError, TimeoutError, ssl.SSLError, smtplib.SMTPException) as error:
                last_error = error
                if attempt < total_attempts:
                    self.sleeper(min(1.0, 0.1 * attempt))
        raise MailDeliveryFailedError(
            "SMTP-операция не выполнена. Проверьте сервер, порт, режим защиты и доступность сети.",
            attempts=total_attempts,
        ) from last_error

    def _check_once(self, client: smtplib.SMTP) -> None:
        code, _ = client.noop()
        if code < 200 or code >= 400:
            raise smtplib.SMTPResponseException(code, b"NOOP rejected")

    @contextmanager
    def _connection(self, settings: MailSettingsORM) -> Iterator[smtplib.SMTP]:
        context = ssl.create_default_context()
        if settings.security_mode == "tls":
            client: smtplib.SMTP = smtplib.SMTP_SSL(
                settings.smtp_host,
                settings.smtp_port,
                timeout=settings.timeout_seconds,
                context=context,
            )
        else:
            client = smtplib.SMTP(
                settings.smtp_host,
                settings.smtp_port,
                timeout=settings.timeout_seconds,
            )
        try:
            client.ehlo_or_helo_if_needed()
            if settings.security_mode == "starttls":
                client.starttls(context=context)
                client.ehlo()
            if settings.smtp_username:
                secret = (os.getenv(MAIL_SECRET_ENV_VAR) or "").strip()
                if not secret:
                    raise MailDeliveryUnavailableError(
                        f"Для SMTP username требуется значение {MAIL_SECRET_ENV_VAR}."
                    )
                client.login(settings.smtp_username, secret)
            yield client
        finally:
            try:
                client.quit()
            except (OSError, smtplib.SMTPException):
                client.close()

    @staticmethod
    def _message(
        settings: MailSettingsORM,
        *,
        recipient: str,
        subject: str,
        body: str,
    ) -> EmailMessage:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = formataddr((settings.sender_name, settings.sender_email))
        message["To"] = recipient
        if settings.reply_to_email:
            message["Reply-To"] = settings.reply_to_email
        message.set_content(body)
        return message
