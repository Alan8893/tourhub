def test_generate_meal_plan_endpoint(
    client,
    override_meal_plan_service,
):
    response = client.post(
        "/api/v1/meal-plans/generate",
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

    meal_plan = data["meal_plan"]
    shopping_list = data["shopping_list"]

    assert meal_plan["name"] == "Altai Trip"

    assert meal_plan["participants"] == 10

    assert meal_plan["days_count"] == 2

    assert len(meal_plan["items"]) == 4

    assert "items" in shopping_list
