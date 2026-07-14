from app.models.recipe import RecipeORM
from app.models.recipe_note import RecipeNoteORM


def test_recipe_notes_are_ordered_by_priority(db_session):
    recipe = RecipeORM(id="recipe-1", name="Solyanka")
    high = RecipeNoteORM(
        id="note-2",
        recipe_id="recipe-1",
        type="serving_tip",
        text="Serve with lemon.",
        priority=20,
    )
    low = RecipeNoteORM(
        id="note-1",
        recipe_id="recipe-1",
        type="cooking_tip",
        text="Add hot pepper if needed.",
        priority=10,
    )

    db_session.add(recipe)
    db_session.add(high)
    db_session.add(low)
    db_session.commit()
    db_session.expire_all()

    loaded_recipe = db_session.query(RecipeORM).filter(RecipeORM.id == "recipe-1").one()

    ordered_priorities = [note.priority for note in loaded_recipe.notes]

    assert ordered_priorities == [10, 20]
    assert loaded_recipe.notes[0].text == "Add hot pepper if needed."
    assert loaded_recipe.notes[1].text == "Serve with lemon."
