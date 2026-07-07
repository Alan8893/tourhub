def test_cors_preflight_allows_frontend_origin(client):
    response = client.options(
        "/api/v1/meta",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_header_present_on_api_response(client):
    response = client.get(
        "/api/v1/meta",
        headers={
            "Origin": "http://localhost:5173",
        },
    )

    assert response.status_code == 200

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
