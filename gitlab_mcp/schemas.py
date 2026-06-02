from pydantic import BaseModel, Field, field_validator

from app.year_filters import validate_year_value


class YearlyReportToolInput(BaseModel):
    """Shared MCP tool input: year plus optional project scope."""

    year: int = Field(..., description="4-digit calendar year, for example 2025")
    project_id_or_path: str | None = Field(
        default=None,
        description="GitLab project ID or URL-encoded path. Omit for instance-wide scope.",
    )

    @field_validator("year")
    @classmethod
    def validate_year_range(cls, value: int) -> int:
        return validate_year_value(value)


class GetIssuesByYearInput(YearlyReportToolInput):
    """MCP tool input for get_issues_by_year."""


class GetMergeRequestsByYearInput(YearlyReportToolInput):
    """MCP tool input for get_merge_requests_by_year."""
