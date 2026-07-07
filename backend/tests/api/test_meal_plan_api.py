def test_generate_meal_plan_endpoint(
    client,
    override_meal_plan_service,
):
    response = client.post(
        "/meal-plans/generate",
        json={
            "name": "Altai Trip",
            "participants": 10,
            "days": 2,
            "meals_per_day": [
                "breakfast",
                "dinner",
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Altai Trip"
    assert data["participants"] == 10
    assert data["days_count"] == 2
    assert len(data["items"]) == 4