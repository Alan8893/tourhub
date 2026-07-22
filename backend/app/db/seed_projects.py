from sqlalchemy.orm import Session

from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM


def seed_projects(session: Session) -> None:
    existing = session.query(ProjectORM).filter(ProjectORM.id == 1).first()
    if existing:
        return

    owner = (
        session.query(UserORM)
        .filter(UserORM.role == "administrator")
        .order_by(UserORM.id.asc())
        .first()
    )
    if owner is None:
        return

    session.add(
        ProjectORM(
            id=1,
            name="Altai Trip 2026",
            participants=10,
            days=7,
            status="draft",
            owner_user_id=owner.id,
        )
    )
    session.commit()
