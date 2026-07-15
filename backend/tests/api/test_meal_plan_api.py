def test_standalone_generation_endpoint_is_not_exposed(client):
    response = client.post(
        "/api/v1/meal-plans/generate",
        json={
            "name": "Altai Trip",
            "participants": 10,
            "days": 2,
            "meals_per_day": ["breakfast", "dinner"],
        },
    )

    assert response.status_code == 404
