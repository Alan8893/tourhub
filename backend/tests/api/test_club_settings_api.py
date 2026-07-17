import base64
from io import BytesIO

from PIL import Image


def _png_data_url() -> str:
    buffer = BytesIO()
    Image.new("RGB", (2, 2), "white").save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def test_club_settings_persist_name_and_logo(client) -> None:
    response = client.get("/api/v1/club-settings")
    assert response.status_code == 200
    assert response.json() == {"club_name": "TourHub", "logo_data_url": None}

    logo_data_url = _png_data_url()
    response = client.put(
        "/api/v1/club-settings",
        json={
            "club_name": "Турклуб Север",
            "logo_data_url": logo_data_url,
            "remove_logo": False,
        },
    )
    assert response.status_code == 200
    assert response.json()["club_name"] == "Турклуб Север"
    assert response.json()["logo_data_url"].startswith("data:image/png;base64,")

    response = client.put(
        "/api/v1/club-settings",
        json={
            "club_name": "Турклуб Северный ветер",
            "logo_data_url": None,
            "remove_logo": False,
        },
    )
    assert response.status_code == 200
    assert response.json()["logo_data_url"].startswith("data:image/png;base64,")

    response = client.put(
        "/api/v1/club-settings",
        json={
            "club_name": "Турклуб Северный ветер",
            "logo_data_url": None,
            "remove_logo": True,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "club_name": "Турклуб Северный ветер",
        "logo_data_url": None,
    }


def test_club_settings_reject_invalid_logo(client) -> None:
    encoded = base64.b64encode(b"not-an-image").decode("ascii")
    response = client.put(
        "/api/v1/club-settings",
        json={
            "club_name": "Турклуб",
            "logo_data_url": f"data:image/png;base64,{encoded}",
            "remove_logo": False,
        },
    )
    assert response.status_code == 400
