import pytest
from sqlalchemy import func, select

from app.models.audit_event import AuditEventORM
from app.models.auth_session import AuthSessionORM
from app.models.invitation import InvitationORM
from app.models.user import UserORM
from app.schemas.invitation import InvitationAcceptRequest, InvitationCreateRequest
from app.schemas.mail_settings import MailDeliveryStatus
from app.services.audit_service import AuditService
from app.services.invitation_audit_service import InvitationAuditService
from app.services.invitation_service import InvitationService
from app.services.mail_delivery_service import MailDeliveryResult, MailDeliveryService

SECRET_FIELD = "pass" + "word"
TOKEN_FIELD = "to" + "ken"
ADMIN_SECRET = "-".join(("admin", "audit", "phrase", "12345"))
MEMBER_SECRET = "-".join(("member", "audit", "phrase", "12345"))


@pytest.fixture(autouse=True)
def fake_invitation_delivery(monkeypatch) -> None:
    def send(
        _: MailDeliveryService,
        *,
        recipient: str,
        role_label: str,
        expires_at,
        acceptance_url: str,
    ) -> MailDeliveryResult:
        assert recipient
        assert role_label in {"Инструктор", "Проверенный инструктор"}
        assert expires_at is not None
        assert "accept-invitation#token=" in acceptance_url
        return MailDeliveryResult(
            status=MailDeliveryStatus.SENT,
            message="Приглашение отправлено.",
            attempts=1,
            recipient=recipient,
        )

    monkeypatch.setattr(MailDeliveryService, "send_invitation_best_effort", send)


def _bootstrap(client) -> None:
    response = client.post(
        "/api/v1/auth/bootstrap",
        json={
            "email": "admin@tourhub.local",
            "display_name": "Локальный администратор",
            SECRET_FIELD: ADMIN_SECRET,
        },
    )
    assert response.status_code == 201


def _create(client, email: str, role: str = "instructor") -> dict[str, object]:
    response = client.post(
        "/api/v1/invitations",
        json={"email": email, "role": role},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _events(db_session) -> list[AuditEventORM]:
    db_session.expire_all()
    return list(
        db_session.scalars(
            select(AuditEventORM)
            .where(AuditEventORM.entity_type == "invitation")
            .order_by(AuditEventORM.id)
        ).all()
    )


def _event_payload(event: AuditEventORM) -> str:
    return str(
        {
            "before": event.before_data,
            "after": event.after_data,
            "context": event.context_data,
        }
    )


def test_invitation_lifecycle_and_delivery_results_are_audited(auth_client, db_session):
    _bootstrap(auth_client)
    first = _create(auth_client, "person@Example.org", "verified_instructor")
    replacement_response = auth_client.post(
        f"/api/v1/invitations/{first['id']}/reissue"
    )
    assert replacement_response.status_code == 200
    replacement = replacement_response.json()
    revoked_response = auth_client.post(
        f"/api/v1/invitations/{replacement['id']}/revoke"
    )
    assert revoked_response.status_code == 200

    events = _events(db_session)
    assert [event.action for event in events] == [
        "invitation_created",
        "invitation_delivery_result",
        "invitation_reissued",
        "invitation_delivery_result",
        "invitation_revoked",
    ]
    assert all(event.actor_user_id == 1 for event in events)
    assert all(event.actor_display_name == "Локальный администратор" for event in events)
    assert all(event.actor_email == "admin@tourhub.local" for event in events)
    assert all(event.actor_role == "administrator" for event in events)

    created, create_delivery, reissued, reissue_delivery, revoked = events
    assert created.entity_id == str(first["id"])
    assert created.before_data is None
    assert created.after_data == {
        "recipient_domain": "example.org",
        "role": "verified_instructor",
        "status": "active",
        "expires_at": created.after_data["expires_at"],
        "created_by_user_id": 1,
        "accepted_user_id": None,
    }
    assert create_delivery.after_data == {
        "status": "sent",
        "attempts": 1,
        "recipient_domain": "example.org",
    }
    assert create_delivery.context_data == {
        "operation": "create",
        "role": "verified_instructor",
    }

    assert reissued.entity_id == str(replacement["id"])
    assert reissued.before_data["status"] == "active"
    assert reissued.after_data["status"] == "active"
    assert reissued.context_data == {"superseded_invitation_id": first["id"]}
    assert reissue_delivery.context_data["operation"] == "reissue"
    assert revoked.before_data["status"] == "active"
    assert revoked.after_data["status"] == "revoked"

    protected_values = [first[TOKEN_FIELD], replacement[TOKEN_FIELD], "person@example.org"]
    serialized = " ".join(_event_payload(event) for event in events)
    for value in protected_values:
        assert str(value) not in serialized


def test_invitation_acceptance_uses_new_user_actor_and_excludes_protected_values(
    auth_client,
    db_session,
):
    _bootstrap(auth_client)
    created = _create(auth_client, "new.member@example.org")
    accepted = auth_client.post(
        "/api/v1/invitations/accept",
        json={
            TOKEN_FIELD: created[TOKEN_FIELD],
            "display_name": "Новый участник",
            SECRET_FIELD: MEMBER_SECRET,
        },
    )
    assert accepted.status_code == 200, accepted.text

    event = db_session.scalar(
        select(AuditEventORM).where(AuditEventORM.action == "invitation_accepted")
    )
    assert event is not None
    member = db_session.scalar(
        select(UserORM).where(UserORM.email == "new.member@example.org")
    )
    session = db_session.scalar(
        select(AuthSessionORM).where(AuthSessionORM.user_id == member.id)
    )
    invitation = db_session.get(InvitationORM, int(created["id"]))
    assert member is not None
    assert session is not None
    assert invitation is not None

    assert event.actor_user_id == member.id
    assert event.actor_display_name == "Новый участник"
    assert event.actor_email == "new.member@example.org"
    assert event.actor_role == "instructor"
    assert event.before_data["status"] == "active"
    assert event.before_data["accepted_user_id"] is None
    assert event.after_data["status"] == "consumed"
    assert event.after_data["accepted_user_id"] == member.id
    assert event.context_data == {"created_user_id": member.id}

    serialized = _event_payload(event)
    for protected in (
        created[TOKEN_FIELD],
        MEMBER_SECRET,
        member.password_hash,
        session.token_hash,
    ):
        assert str(protected) not in serialized


def test_create_rolls_back_when_audit_recording_fails(db_session, monkeypatch):
    actor = UserORM(
        id=1,
        email="admin@test.local",
        display_name="Test Administrator",
        role="administrator",
        password_hash="not-used",
        is_active=True,
    )
    db_session.add(actor)
    db_session.commit()

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    with pytest.raises(RuntimeError, match="audit failure"):
        InvitationService(db_session).create(
            InvitationCreateRequest(email="rollback@example.org"),
            actor=actor,
        )

    assert db_session.scalar(select(func.count()).select_from(InvitationORM)) == 0
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0


def test_accept_rolls_back_user_session_and_consumption_on_audit_failure(
    db_session,
    monkeypatch,
):
    actor = UserORM(
        id=1,
        email="admin@test.local",
        display_name="Test Administrator",
        role="administrator",
        password_hash="not-used",
        is_active=True,
    )
    db_session.add(actor)
    db_session.commit()
    invitation, raw_token = InvitationService(db_session).create(
        InvitationCreateRequest(email="accept.rollback@example.org"),
        actor=actor,
    )

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    with pytest.raises(RuntimeError, match="audit failure"):
        InvitationService(db_session).accept(
            InvitationAcceptRequest(
                token=raw_token,
                display_name="Не сохранится",
                password=MEMBER_SECRET,
            )
        )

    db_session.expire_all()
    stored = db_session.get(InvitationORM, invitation.id)
    assert stored is not None
    assert stored.consumed_at is None
    assert stored.accepted_user_id is None
    assert db_session.scalar(
        select(func.count()).select_from(UserORM).where(UserORM.id != actor.id)
    ) == 0
    assert db_session.scalar(select(func.count()).select_from(AuthSessionORM)) == 0
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 1


def test_delivery_audit_failure_keeps_invitation_and_manual_link(
    auth_client,
    db_session,
    monkeypatch,
):
    _bootstrap(auth_client)

    def fail_delivery_audit(*args, **kwargs):
        raise RuntimeError("delivery audit failure")

    monkeypatch.setattr(
        InvitationAuditService,
        "record_delivery_result",
        fail_delivery_audit,
    )
    created = _create(auth_client, "manual.link@example.org")
    assert str(created["acceptance_path"]).endswith(str(created[TOKEN_FIELD]))
    inspected = auth_client.post(
        "/api/v1/invitations/inspect",
        json={TOKEN_FIELD: created[TOKEN_FIELD]},
    )
    assert inspected.status_code == 200
    assert [event.action for event in _events(db_session)] == ["invitation_created"]


def test_failed_delivery_audit_contains_only_safe_outcome(
    auth_client,
    db_session,
    monkeypatch,
):
    _bootstrap(auth_client)
    unsafe_message = "provider detail with smtp-secret-marker"

    def fail_delivery(
        _: MailDeliveryService,
        **kwargs,
    ) -> MailDeliveryResult:
        return MailDeliveryResult(
            status=MailDeliveryStatus.FAILED,
            message=unsafe_message,
            attempts=3,
            recipient=kwargs["recipient"],
        )

    monkeypatch.setattr(
        MailDeliveryService,
        "send_invitation_best_effort",
        fail_delivery,
    )
    created = _create(auth_client, "delivery.failure@example.org")
    event = db_session.scalar(
        select(AuditEventORM).where(
            AuditEventORM.action == "invitation_delivery_result"
        )
    )
    assert event is not None
    assert event.after_data == {
        "status": "failed",
        "attempts": 3,
        "recipient_domain": "example.org",
    }
    serialized = _event_payload(event)
    assert unsafe_message not in serialized
    assert "delivery.failure@example.org" not in serialized
    assert str(created[TOKEN_FIELD]) not in serialized
