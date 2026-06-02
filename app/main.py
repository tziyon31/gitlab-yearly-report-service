import json
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Query
from fastapi.responses import JSONResponse

from app.reports import build_issues_report, build_merge_requests_report
from app.schemas import IssuesReport, MergeRequestsReport
from app.settings import Settings, get_settings
from app.year_filters import parse_year_query


class PrettyJSONResponse(JSONResponse):
    """Return human-readable, indented JSON so reports are easy to read."""

    def render(self, content: Any) -> bytes:
        return json.dumps(content, indent=2, ensure_ascii=False).encode("utf-8")


app = FastAPI(
    title="GitLab Yearly Report Service",
    version="0.1.0",
    default_response_class=PrettyJSONResponse,
)

# Fail fast when the app module is loaded (missing GITLAB_URL / GITLAB_TOKEN).
get_settings()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/issues", response_model=IssuesReport)
def issues(
    settings: Annotated[Settings, Depends(get_settings)],
    year: str | None = Query(default=None),
    project: str | None = Query(default=None),
) -> IssuesReport:
    parsed_year = parse_year_query(year)

    return build_issues_report(
        settings=settings,
        year=parsed_year,
        project_id_or_path=project,
    )


@app.get("/merge-requests", response_model=MergeRequestsReport)
def merge_requests(
    settings: Annotated[Settings, Depends(get_settings)],
    year: str | None = Query(default=None),
    project: str | None = Query(default=None),
) -> MergeRequestsReport:
    parsed_year = parse_year_query(year)

    return build_merge_requests_report(
        settings=settings,
        year=parsed_year,
        project_id_or_path=project,
    )
