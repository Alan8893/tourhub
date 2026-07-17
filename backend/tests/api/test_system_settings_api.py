import base64
from io import BytesIO

from PIL import Image
from sqlalchemy import func, select

from app.models.system_settings_history import SystemSettingsHistoryORM
from app.schemas.club_settings import ClubSettingsDetailUpdateRequest
from app.services.club_settings_service import ClubSettingsService


def _image_data_url(image_format: str = "PNG") -> str:
    buffer = BytesIO()
    Image.new("RGB", (4, 4), "white").save(buffer, format=image_format)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    mime_type = {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp",
    }[image_format]
    return f"data:{mime_type};base64,{encoded}"


def _update_payload(*, version: int, club_name: str = "Турклуб Север") -> dict[str, object]:
    return {
        "expected_version": version,
        "club_name": club_name,
        "short_name": "Север",
        "legal_name": "Региональная организация Турклуб Север",
        "description": "Походы и обучение туристов.",
        "address": "Москва, ул. Туристическая, 1",
        "phone": "+7 900 000-00-00",
        "email": "club@example.org",
        "website": "https://club.example.org",
        "timezone": "Europe/Moscow",
        "city": "Москва",
        "region": "Москва",
        "social_links": [
            {"label": "Telegram", "url": "https://t.me/tourclub"},
            {"label": "VK", "url": "https://vk.com/tourclub"},
        ],
        "images": {
            "main_logo": {"data_url": _image_data_url(), "remove": False},
            "favicon": {"data_url": _image_data_url("WEBP"), "remove": False},
        },
    }


def test_system_settings_persist_profile_images_and_history(client) -> None:
    response = client.get("/api/v1/settings/club")
    assert response.status_code == 200
    initial = response.json()
    assert initial["version"] == 1
    assert initial["club_name"] == "TourHub"
    assert initial["short_name"] is None
    assert initial["social_links"] == []
    assert initial["images"]["main_logo_data_url"] is None

    response = client.put(
        "/api/v1/settings/club",
        json=_update_payload(version=initial["version"]),
    )
    assert response.status_code == 200
    settings = response.json()
    assert settings["version"] == 2
    assert settings["club_name"] == "Турклуб Север"
    assert settings["short_name"] == "Север"
    assert settings["website"] == "https://club.example.org"
    assert settings["social_links"][0] == {
        "label": "Telegram",
        "url": "https://t.me/tourclub",
    }
    assert settings["images"]["main_logo_data_url"].startswith("data:image/png;base64,")
    assert settings["images"]["favicon_data_url"].startswith("data:image/webp;base64,")

    response = client.get("/api/v1/settings/club")
    assert response.status_code == 200
    assert response.json()["version"] == 2
    assert response.json()["description"] == "Походы и обучение туристов."

    response = client.get("/api/v1/settings/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 1
    assert history[0]["actor_label"] == "Локальный администратор"
    assert history[0]["settings_version"] == 2
    assert "images.main_logo" in history[0]["changed_fields"]
    assert "images.favicon" in history[0]["changed_fields"]
    assert "data:image" not in str(history[0])


def test_system_settings_reject_stale_version_without_overwrite(client) -> None:
    response = client.put(
        "/api/v1/settings/club",
        json=_update_payload(version=1),
    )
    assert response.status_code == 200

    stale_payload = _update_payload(version=1, club_name="Устаревшее название")
    response = client.put("/api/v1/settings/club", json=stale_payload)
    assert response.status_code == 409
    assert "stale" in response.json()["detail"]

    response = client.get("/api/v1/settings/club")
    assert response.status_code == 200
    assert response.json()["club_name"] == "Турклуб Север"
    assert response.json()["version"] == 2


def test_system_settings_remove_image_and_trim_optional_values(client) -> None:
    response = client.put(
        "/api/v1/settings/club",
        json=_update_payload(version=1),
    )
    assert response.status_code == 200

    payload = _update_payload(version=2)
    payload.update(
        {
            "short_name": "   ",
            "legal_name": None,
            "description": None,
            "address": None,
            "phone": None,
            "email": None,
            "website": None,
            "timezone": None,
            "city": None,
            "region": None,
            "social_links": [],
            "images": {
                "main_logo": {"data_url": None, "remove": True},
                "favicon": {"data_url": None, "remove": True},
            },
        }
    )
    response = client.put("/api/v1/settings/club", json=payload)
    assert response.status_code == 200
    settings = response.json()
    assert settings["version"] == 3
    assert settings["short_name"] is None
    assert settings["social_links"] == []
    assert settings["images"]["main_logo_data_url"] is None
    assert settings["images"]["favicon_data_url"] is None


def test_system_settings_validate_urls_timezone_and_duplicates(client) -> None:
    payload = _update_payload(version=1)
    payload["website"] = "ftp://club.example.org"
    response = client.put("/api/v1/settings/club", json=payload)
    assert response.status_code == 400
    assert "http or https" in response.json()["detail"]

    payload = _update_payload(version=1)
    payload["timezone"] = "Not/A-Timezone"
    response = client.put("/api/v1/settings/club", json=payload)
    assert response.status_code == 400
    assert "IANA timezone" in response.json()["detail"]

    payload = _update_payload(version=1)
    payload["social_links"] = [
        {"label": "Telegram", "url": "https://t.me/tourclub"},
        {"label": "telegram", "url": "https://t.me/tourclub"},
    ]
    response = client.put("/api/v1/settings/club", json=payload)
    assert response.status_code == 400
    assert "unique" in response.json()["detail"]


def test_system_settings_history_keeps_latest_two_hundred(db_session) -> None:
    service = ClubSettingsService(db_session)
    settings = service.get()
    for version in range(2, 207):
        db_session.add(
            SystemSettingsHistoryORM(
                section="club",
                actor_label="Локальный администратор",
                action="updated",
                changed_fields=["club_name"],
                settings_version=version,
            )
        )
    db_session.commit()

    service.update_details(
        ClubSettingsDetailUpdateRequest(
            expected_version=settings.version,
            club_name="Турклуб Полюс",
        )
    )

    count = db_session.scalar(select(func.count(SystemSettingsHistoryORM.id)))
    assert count == 200
