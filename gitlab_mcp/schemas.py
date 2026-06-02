from pydantic import BaseModel, Field, field_validator

from app.year_filters import MAX_YEAR, MIN_YEAR


class GetIssuesByYearInput(BaseModel):
    """MCP tool input for get_issues_by_year."""

    year: int = Field(..., description="4-digit calendar year, for example 2025")
    project_id_or_path: str | None = Field(
        default=None,
        description="GitLab project ID or URL-encoded path. Omit for instance-wide scope.",
    )

    @field_validator("year")
    @classmethod
    def validate_year_range(cls, value: int) -> int:
        if value < MIN_YEAR or value > MAX_YEAR:
            raise ValueError(f"year must be between {MIN_YEAR} and {MAX_YEAR}")
        return value


class GetMergeRequestsByYearInput(BaseModel):
    """MCP tool input for get_merge_requests_by_year."""

    year: int = Field(..., description="4-digit calendar year, for example 2025")
    project_id_or_path: str | None = Field(
        default=None,
        description="GitLab project ID or URL-encoded path. Omit for instance-wide scope.",
    )

    @field_validator("year")
    @classmethod
    def validate_year_range(cls, value: int) -> int:
        if value < MIN_YEAR or value > MAX_YEAR:
            raise ValueError(f"year must be between {MIN_YEAR} and {MAX_YEAR}")
        return value
