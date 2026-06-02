"""MCP server exposing GitLab yearly report tools."""

from collections.abc import Callable
from typing import Any

from fastapi import HTTPException
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from app.reports import build_issues_report, build_merge_requests_report
from app.schemas import IssuesReport, MergeRequestsReport
from app.settings import Settings, get_settings
from gitlab_mcp.schemas import GetIssuesByYearInput, GetMergeRequestsByYearInput

mcp = FastMCP(
    "gitlab-yearly-report-service",
    instructions=(
        "Read-only GitLab yearly reports for issues and merge requests. "
        "Configure GITLAB_URL and GITLAB_TOKEN. Optional: ENABLE_MEMBERSHIP_FALLBACK."
    ),
)


settings: Settings = get_settings()


def _run_report_tool(
    build_report: Callable[..., IssuesReport | MergeRequestsReport],
    tool_input: BaseModel,
    *,
    app_settings: Settings,
) -> dict[str, Any]:
    """Build a report via app.reports and return JSON-serializable dict for MCP."""
    try:
        report = build_report(
            settings=app_settings,
            year=tool_input.year,
            project_id_or_path=tool_input.project_id_or_path,
        )
        return report.model_dump(mode="json")
    except ValidationError as error:
        raise ValueError(str(error)) from error
    except HTTPException as error:
        raise RuntimeError(f"{error.status_code}: {error.detail}") from error


@mcp.tool(
    name="get_issues_by_year",
    description=(
        "Return GitLab issues created in the given year. "
        "Omit project_id_or_path for instance-wide scope (token permissions apply)."
    ),
)
def get_issues_by_year(
    year: int,
    project_id_or_path: str | None = None,
) -> dict[str, Any]:
    tool_input = GetIssuesByYearInput(
        year=year,
        project_id_or_path=project_id_or_path,
    )
    return _run_report_tool(build_issues_report, tool_input, app_settings=settings)


@mcp.tool(
    name="get_merge_requests_by_year",
    description=(
        "Return GitLab merge requests created in the given year. "
        "Omit project_id_or_path for instance-wide scope (token permissions apply)."
    ),
)
def get_merge_requests_by_year(
    year: int,
    project_id_or_path: str | None = None,
) -> dict[str, Any]:
    tool_input = GetMergeRequestsByYearInput(
        year=year,
        project_id_or_path=project_id_or_path,
    )
    return _run_report_tool(build_merge_requests_report, tool_input, app_settings=settings)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
