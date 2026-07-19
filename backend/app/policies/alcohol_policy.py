import re
import unicodedata
from collections.abc import Iterable
from typing import Protocol


class AlcoholPolicyViolation(ValueError):
    """Raised when a Product, Recipe, Dish, or import row references alcohol."""


class ProductLike(Protocol):
    name: str
    category: str | None
    is_archived: bool


class RecipeComponentLike(Protocol):
    product: ProductLike


class RecipeLike(Protocol):
    name: str
    is_archived: bool
    components: Iterable[RecipeComponentLike]


_TOKEN_PATTERN = re.compile(r"[\w]+", flags=re.UNICODE)

_EXACT_TERMS = frozenset(
    {
        "алкоголь",
        "алкоголя",
        "алкогольный",
        "алкогольная",
        "алкогольное",
        "алкогольные",
        "спирт",
        "спирта",
        "спиртное",
        "спиртные",
        "водка",
        "водки",
        "водку",
        "водкой",
        "вино",
        "вина",
        "вину",
        "вином",
        "вине",
        "винный",
        "винная",
        "винное",
        "винные",
        "пиво",
        "пива",
        "пиву",
        "пивом",
        "пивной",
        "пивная",
        "пивное",
        "пивные",
        "сидр",
        "сидра",
        "шампанское",
        "шампанского",
        "коньяк",
        "коньяка",
        "виски",
        "ром",
        "рома",
        "джин",
        "джина",
        "текила",
        "текилы",
        "ликер",
        "ликера",
        "вермут",
        "вермута",
        "медовуха",
        "медовухи",
        "самогон",
        "самогона",
        "настойка",
        "настойки",
        "наливка",
        "наливки",
        "мартини",
        "саке",
        "бренди",
        "бурбон",
        "абсент",
        "кальвадос",
        "граппа",
        "портвейн",
        "херес",
        "мадера",
        "beer",
        "wine",
        "vodka",
        "cider",
        "champagne",
        "cognac",
        "whisky",
        "whiskey",
        "rum",
        "gin",
        "tequila",
        "liqueur",
        "liquor",
        "vermouth",
        "mead",
        "moonshine",
        "sake",
        "brandy",
        "bourbon",
        "absinthe",
    }
)


class AlcoholPolicy:
    """One Backend rule for alcohol classification and rejection.

    Classification is deliberately deterministic and text-based because the current
    Product/Dish schemas expose names and categories rather than a separate alcohol
    flag. Tokens are matched as complete normalized words, so terms such as ``ром``
    do not match unrelated words such as ``ромашка``.
    """

    ERROR_MESSAGE = "Алкоголь запрещён в TourHub без исключений."

    @staticmethod
    def normalized_tokens(*values: str | None) -> tuple[str, ...]:
        combined = " ".join(value for value in values if value)
        normalized = unicodedata.normalize("NFKC", combined).casefold().replace("ё", "е")
        return tuple(_TOKEN_PATTERN.findall(normalized))

    @classmethod
    def contains_prohibited_reference(cls, *values: str | None) -> bool:
        return any(token in _EXACT_TERMS for token in cls.normalized_tokens(*values))

    @classmethod
    def require_product_allowed(cls, *, name: str, category: str | None) -> None:
        if cls.contains_prohibited_reference(name, category):
            raise AlcoholPolicyViolation(cls.ERROR_MESSAGE)

    @classmethod
    def require_recipe_name_allowed(cls, name: str) -> None:
        if cls.contains_prohibited_reference(name):
            raise AlcoholPolicyViolation(cls.ERROR_MESSAGE)

    @classmethod
    def require_dish_name_allowed(cls, name: str) -> None:
        if cls.contains_prohibited_reference(name):
            raise AlcoholPolicyViolation(cls.ERROR_MESSAGE)

    @classmethod
    def require_product_record_allowed(cls, product: ProductLike) -> None:
        cls.require_product_allowed(name=product.name, category=product.category)
        if product.is_archived:
            raise AlcoholPolicyViolation(
                "Архивный продукт нельзя добавлять в новый или изменяемый рецепт."
            )

    @classmethod
    def require_recipe_record_allowed(cls, recipe: RecipeLike) -> None:
        cls.require_recipe_name_allowed(recipe.name)
        if recipe.is_archived:
            raise AlcoholPolicyViolation(
                "Архивный рецепт нельзя использовать в новом или изменяемом блюде."
            )
        for component in recipe.components:
            cls.require_product_record_allowed(component.product)
