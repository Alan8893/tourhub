import pytest

from app.engines.meal_schedule import MealScheduleEngine


@pytest.fixture
def engine():
    return MealScheduleEngine()


def test_full_day_schedule(engine):
    result = engine.build(days=3, start_meal="breakfast", end_meal="dinner")
    expected = ["breakfast", "snack", "lunch", "dinner"]
    assert result[0].meals == expected
    assert result[1].meals == expected
    assert result[2].meals == expected


def test_partial_start_and_end(engine):
    result = engine.build(days=3, start_meal="snack", end_meal="lunch")
    assert result[0].meals == ["snack", "lunch", "dinner"]
    assert result[1].meals == ["breakfast", "snack", "lunch", "dinner"]
    assert result[2].meals == ["breakfast", "snack", "lunch"]


def test_one_day_single_meal(engine):
    result = engine.build(days=1, start_meal="snack", end_meal="snack")
    assert result[0].meals == ["snack"]


def test_one_day_range_uses_domain_order(engine):
    result = engine.build(days=1, start_meal="snack", end_meal="dinner")
    assert result[0].meals == ["snack", "lunch", "dinner"]


def test_one_day_cannot_finish_before_start(engine):
    with pytest.raises(ValueError):
        engine.build(days=1, start_meal="dinner", end_meal="breakfast")


def test_invalid_days(engine):
    with pytest.raises(ValueError):
        engine.build(days=0, start_meal="lunch", end_meal="lunch")
