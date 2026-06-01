from app.gitlab_client import encode_project_id_or_path, get_paginated_from_gitlab
from app.settings import Settings
from app.year_filters import build_year_filter_params


def get_issues_by_year(
    settings: Settings,
    year: int,
    project_id_or_path: str | None = None,
) -> list[dict]:
    params = build_year_filter_params(year)

    if project_id_or_path:
        encoded_project = encode_project_id_or_path(project_id_or_path)
        path = f"/projects/{encoded_project}/issues"
    else:
        path = "/issues"

    return get_paginated_from_gitlab(
        settings=settings,
        path=path,
        params=params,
    )


def get_merge_requests_by_year(
    settings: Settings,
    year: int,
    project_id_or_path: str | None = None,
) -> list[dict]:
    params = build_year_filter_params(year)

    if project_id_or_path:
        encoded_project = encode_project_id_or_path(project_id_or_path)
        path = f"/projects/{encoded_project}/merge_requests"
    else:
        path = "/merge_requests"

    return get_paginated_from_gitlab(
        settings=settings,
        path=path,
        params=params,
    )
