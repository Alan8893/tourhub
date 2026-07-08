from sqlalchemy.orm import Session

from app.modules.projects.models.project import ProjectORM



def seed_projects(session: Session) -> None:
    existing = session.query(ProjectORM).filter(ProjectORM.id == 1).first()

    if existing:
        return

    session.add(
        ProjectORM(
            id=1,
            name="Altai Trip 2026",
            participants=10,
            days=7,
            status="draft",
        )
    )

    session.commit()
