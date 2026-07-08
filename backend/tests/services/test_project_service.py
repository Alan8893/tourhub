from app.modules.projects.service import ProjectService


class FakeRepository:
    def get_by_id(self, project_id: int):
        return type(
            "Project",
            (),
            {
                "id": project_id,
                "name": "Altai Trip 2026",
                "participants": 10,
                "days": 7,
                "status": "draft",
            },
        )()


def test_project_service_maps_project():
    service = ProjectService(FakeRepository())

    result = service.get_project(1)

    assert result.name == "Altai Trip 2026"
    assert result.days == 7
