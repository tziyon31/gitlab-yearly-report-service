"""MCP server exposing GitLab yearly report tools."""

from typing import Any

from fastapi import HTTPException
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from app.settings import get_settings
from gitlab_mcp.handlers import handle_get_issues_by_year, handle_get_merge_requests_by_year
from gitlab_mcp.schemas import GetIssuesByYearInput, GetMergeRequestsByYearInput

mcp = FastMCP(
    "gitlab-yearly-report-service",
    instructions=(
        "Read-only GitLab yearly reports for issues and merge requests. "
        "Configure GITLAB_URL and GITLAB_TOKEN. Optional: ENABLE_MEMBERSHIP_FALLBACK."
    ),
)


def _report_to_dict(handler, tool_input) -> dict[str, Any]:
    try:
        settings = get_settings()
        report = handler(settings, tool_input)
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
    return _report_to_dict(handle_get_issues_by_year, tool_input)


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
    return _report_to_dict(handle_get_merge_requests_by_year, tool_input)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
