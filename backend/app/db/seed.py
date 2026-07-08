from app.core.database import SessionLocal

from app.db.seed_products import seed_products
from app.db.seed_recipes import seed_recipes
from app.db.seed_dishes import seed_dishes
from app.db.seed_projects import seed_projects


def run_seed() -> None:
    """
    Execute database seed.

    Order:
    1. Products
    2. Recipes and ingredients
    3. Dishes
    4. Projects
    """

    session = SessionLocal()

    try:
        print("Seeding products...")
        seed_products(session)

        print("Seeding recipes...")
        seed_recipes(session)

        print("Seeding dishes...")
        seed_dishes(session)

        print("Seeding projects...")
        seed_projects(session)

        print("Seed completed successfully.")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
