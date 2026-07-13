from app.models.recipe_component_type import RecipeComponentType


def test_recipe_component_types_contract():
    assert RecipeComponentType.BASE.value == "base"
    assert RecipeComponentType.COOKING.value == "cooking"
    assert RecipeComponentType.OPTIONAL.value == "optional"
    assert RecipeComponentType.SERVING_ADD_ON.value == "serving_add_on"


def test_optional_components_are_separate_from_base_components():
    assert (
        RecipeComponentType.OPTIONAL
        != RecipeComponentType.BASE
    )
