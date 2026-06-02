from gitlab_mcp.schemas import GetIssuesByYearInput, GetMergeRequestsByYearInput
from app.reports import build_issues_report, build_merge_requests_report
from app.schemas import IssuesReport, MergeRequestsReport
from app.settings import Settings


def handle_get_issues_by_year(
    settings: Settings,
    tool_input: GetIssuesByYearInput,
) -> IssuesReport:
    return build_issues_report(
        settings=settings,
        year=tool_input.year,
        project_id_or_path=tool_input.project_id_or_path,
    )


def handle_get_merge_requests_by_year(
    settings: Settings,
    tool_input: GetMergeRequestsByYearInput,
) -> MergeRequestsReport:
    return build_merge_requests_report(
        settings=settings,
        year=tool_input.year,
        project_id_or_path=tool_input.project_id_or_path,
    )
