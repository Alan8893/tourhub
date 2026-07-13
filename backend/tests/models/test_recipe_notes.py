from datetime import datetime

from app.models.recipe_note import RecipeNoteORM
from app.models.recipe_note_type import RecipeNoteType


def test_recipe_note_types_contract():
    assert RecipeNoteType.COOKING_TIP.value == "cooking_tip"
    assert RecipeNoteType.EXPEDITION_TIP.value == "expedition_tip"
    assert RecipeNoteType.SERVING_TIP.value == "serving_tip"


def test_recipe_note_model_defaults():
    note = RecipeNoteORM(
        id="note-1",
        recipe_id="recipe-1",
        text="Add lemon at the end.",
    )

    assert note.type == RecipeNoteType.COOKING_TIP.value
    assert note.priority == 100
    assert isinstance(note.created_at, datetime)


def test_recipe_note_model_can_store_custom_type_and_priority():
    note = RecipeNoteORM(
        id="note-2",
        recipe_id="recipe-1",
        type=RecipeNoteType.EXPEDITION_TIP.value,
        text="Works well in cold weather.",
        priority=10,
    )

    assert note.type == RecipeNoteType.EXPEDITION_TIP.value
    assert note.priority == 10
