from pydantic import BaseModel


class IssueItem(BaseModel):
    id: int
    iid: int
    project_id: int
    title: str
    state: str
    created_at: str
    web_url: str | None = None


class MergeRequestItem(BaseModel):
    id: int
    iid: int
    project_id: int
    title: str
    state: str
    created_at: str
    source_branch: str
    target_branch: str
    web_url: str


class IssuesReport(BaseModel):
    year: int
    project: str | None = None
    count: int
    items: list[IssueItem]


class MergeRequestsReport(BaseModel):
    year: int
    project: str | None = None
    count: int
    items: list[MergeRequestItem]
