from app.gitlab_client import get_paginated_from_gitlab
from app.settings import Settings


def list_membership_project_ids(settings: Settings) -> list[int]:
    projects = get_paginated_from_gitlab(
        settings=settings,
        path="/projects",
        params={
            "membership": "true",
            "simple": "true",
            "order_by": "id",
            "sort": "asc",
            "per_page": 100,
        },
    )

    project_ids: list[int] = []
    for project in projects:
        project_id = project.get("id")
        if isinstance(project_id, int):
            project_ids.append(project_id)

    return project_ids


def fetch_by_membership_enumeration(
    settings: Settings,
    resource: str,
    params: dict[str, str | int],
) -> list[dict]:
    aggregated_items: list[dict] = []

    for project_id in list_membership_project_ids(settings):
        project_items = get_paginated_from_gitlab(
            settings=settings,
            path=f"/projects/{project_id}/{resource}",
            params=params,
        )
        aggregated_items.extend(project_items)

    return aggregated_items
