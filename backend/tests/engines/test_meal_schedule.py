import pytest

from app.engines.meal_schedule import MealScheduleEngine


@pytest.fixture

def engine():
    return MealScheduleEngine()


def test_full_day_schedule(engine):
    result = engine.build(
        days=3,
        start_meal="breakfast",
        end_meal="dinner",
    )

    assert result[0].meals == ["breakfast", "lunch", "dinner"]
    assert result[1].meals == ["breakfast", "lunch", "dinner"]
    assert result[2].meals == ["breakfast", "lunch", "dinner"]


def test_partial_start_and_end(engine):
    result = engine.build(
        days=3,
        start_meal="dinner",
        end_meal="lunch",
    )

    assert result[0].meals == ["dinner"]
    assert result[1].meals == ["breakfast", "lunch", "dinner"]
    assert result[2].meals == ["breakfast", "lunch"]


def test_one_day_lunch_only(engine):
    result = engine.build(
        days=1,
        start_meal="lunch",
        end_meal="lunch",
    )

    assert result[0].meals == ["lunch"]


def test_invalid_days(engine):
    with pytest.raises(ValueError):
        engine.build(
            days=0,
            start_meal="lunch",
            end_meal="lunch",
        )
