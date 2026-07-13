from app.models.recipe import RecipeORM
from app.models.recipe_note import RecipeNoteORM


def test_recipe_notes_are_ordered_by_priority():
    recipe = RecipeORM(id="recipe-1", name="Solyanka")
    high = RecipeNoteORM(
        id="note-2",
        recipe_id="recipe-1",
        text="Serve with lemon.",
        priority=20,
    )
    low = RecipeNoteORM(
        id="note-1",
        recipe_id="recipe-1",
        text="Add hot pepper if needed.",
        priority=10,
    )

    recipe.notes = [high, low]

    ordered_priorities = [note.priority for note in recipe.notes]

    assert ordered_priorities == [10, 20]
    assert recipe.notes[0].text == "Add hot pepper if needed."
    assert recipe.notes[1].text == "Serve with lemon."
