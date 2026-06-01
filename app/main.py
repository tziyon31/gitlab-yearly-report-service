from fastapi import FastAPI, Query

from app.mappers import map_issue, map_merge_request
from app.reports import get_issues_by_year, get_merge_requests_by_year
from app.schemas import IssuesReport, MergeRequestsReport
from app.settings import get_settings
from app.year_filters import parse_year_query


# Validate required environment variables when the application starts.
settings = get_settings()

app = FastAPI(
    title="GitLab Yearly Report Service",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/issues", response_model=IssuesReport)
def issues(
    year: str | None = Query(default=None),
    project: str | None = Query(default=None),
) -> IssuesReport:
    parsed_year = parse_year_query(year)

    raw_issues = get_issues_by_year(
        settings=settings,
        year=parsed_year,
        project_id_or_path=project,
    )

    items = [map_issue(raw_issue) for raw_issue in raw_issues]

    return IssuesReport(
        year=parsed_year,
        project=project,
        count=len(items),
        items=items,
    )


@app.get("/merge-requests", response_model=MergeRequestsReport)
def merge_requests(
    year: str | None = Query(default=None),
    project: str | None = Query(default=None),
) -> MergeRequestsReport:
    parsed_year = parse_year_query(year)

    raw_merge_requests = get_merge_requests_by_year(
        settings=settings,
        year=parsed_year,
        project_id_or_path=project,
    )

    items = [
        map_merge_request(raw_merge_request)
        for raw_merge_request in raw_merge_requests
    ]

    return MergeRequestsReport(
        year=parsed_year,
        project=project,
        count=len(items),
        items=items,
    )
