import pytest

from app.policies.alcohol_policy import AlcoholPolicy, AlcoholPolicyViolation


@pytest.mark.parametrize(
    ("name", "category"),
    [
        ("Водка", None),
        ("Красное вино", "Напитки"),
        ("Сидр яблочный", None),
        ("Tour beer", None),
        ("Минеральная вода", "Алкогольные напитки"),
    ],
)
def test_alcohol_policy_rejects_prohibited_product_text(
    name: str,
    category: str | None,
) -> None:
    with pytest.raises(AlcoholPolicyViolation, match="Алкоголь запрещён"):
        AlcoholPolicy.require_product_allowed(name=name, category=category)


@pytest.mark.parametrize(
    "name",
    [
        "Ромашка сушёная",
        "Виноградный сок",
        "Пивные дрожжи для хлеба",
        "Винный уксус",
        "Чай лесной",
    ],
)
def test_alcohol_policy_does_not_use_unsafe_substring_matching(name: str) -> None:
    AlcoholPolicy.require_product_allowed(name=name, category="Продукты")


def test_alcohol_policy_normalizes_case_punctuation_and_yo() -> None:
    assert AlcoholPolicy.contains_prohibited_reference("ЛИКЁР, сливочный") is True
    assert AlcoholPolicy.contains_prohibited_reference("Чай с ромом") is True
    assert AlcoholPolicy.contains_prohibited_reference("ромашка") is False
