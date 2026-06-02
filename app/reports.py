import logging

from fastapi import HTTPException

from app.fallback_enumeration import fetch_by_membership_enumeration
from app.gitlab_client import encode_project_id_or_path, get_paginated_from_gitlab
from app.mappers import map_issue, map_merge_request
from app.schemas import IssuesReport, MergeRequestsReport
from app.settings import Settings
from app.year_filters import build_year_filter_params

logger = logging.getLogger(__name__)


def _raise_global_scope_failure_with_fallback_hint(error: HTTPException) -> None:
    raise HTTPException(
        status_code=error.status_code,
        detail=(
            f"{error.detail}. Global scope query failed before fallback. "
            "To enable fallback enumeration over membership=true projects, "
            "set ENABLE_MEMBERSHIP_FALLBACK=true."
        ),
    ) from error


def get_issues_by_year(
    settings: Settings,
    year: int,
    project_id_or_path: str | None = None,
) -> list[dict]:
    params = build_year_filter_params(year)

    if project_id_or_path:
        encoded_project = encode_project_id_or_path(project_id_or_path)
        path = f"/projects/{encoded_project}/issues"
        return get_paginated_from_gitlab(
            settings=settings,
            path=path,
            params=params,
        )

    try:
        return get_paginated_from_gitlab(
            settings=settings,
            path="/issues",
            params=params,
        )
    except HTTPException as error:
        if error.status_code in {502, 504}:
            if not settings.enable_membership_fallback:
                _raise_global_scope_failure_with_fallback_hint(error)
            logger.warning(
                "Global /issues query failed with %s. "
                "Falling back to membership=true project enumeration.",
                error.status_code,
            )
            return fetch_by_membership_enumeration(
                settings=settings,
                resource="issues",
                params=params,
            )
        raise


def get_merge_requests_by_year(
    settings: Settings,
    year: int,
    project_id_or_path: str | None = None,
) -> list[dict]:
    params = build_year_filter_params(year)

    if project_id_or_path:
        encoded_project = encode_project_id_or_path(project_id_or_path)
        path = f"/projects/{encoded_project}/merge_requests"
        return get_paginated_from_gitlab(
            settings=settings,
            path=path,
            params=params,
        )

    try:
        return get_paginated_from_gitlab(
            settings=settings,
            path="/merge_requests",
            params=params,
        )
    except HTTPException as error:
        if error.status_code in {502, 504}:
            if not settings.enable_membership_fallback:
                _raise_global_scope_failure_with_fallback_hint(error)
            logger.warning(
                "Global /merge_requests query failed with %s. "
                "Falling back to membership=true project enumeration.",
                error.status_code,
            )
            return fetch_by_membership_enumeration(
                settings=settings,
                resource="merge_requests",
                params=params,
            )
        raise


def build_issues_report(
    settings: Settings,
    year: int,
    project_id_or_path: str | None = None,
) -> IssuesReport:
    raw_issues = get_issues_by_year(
        settings=settings,
        year=year,
        project_id_or_path=project_id_or_path,
    )

    items = [map_issue(raw_issue) for raw_issue in raw_issues]

    return IssuesReport(
        year=year,
        project=project_id_or_path,
        count=len(items),
        items=items,
    )


def build_merge_requests_report(
    settings: Settings,
    year: int,
    project_id_or_path: str | None = None,
) -> MergeRequestsReport:
    raw_merge_requests = get_merge_requests_by_year(
        settings=settings,
        year=year,
        project_id_or_path=project_id_or_path,
    )

    items = [map_merge_request(raw_mr) for raw_mr in raw_merge_requests]

    return MergeRequestsReport(
        year=year,
        project=project_id_or_path,
        count=len(items),
        items=items,
    )
