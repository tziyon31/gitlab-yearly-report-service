from app.schemas import IssueItem, MergeRequestItem


def map_issue(raw_issue: dict) -> IssueItem:
    return IssueItem(
        id=raw_issue["id"],
        iid=raw_issue["iid"],
        project_id=raw_issue["project_id"],
        title=raw_issue["title"],
        state=raw_issue["state"],
        created_at=raw_issue["created_at"],
        web_url=raw_issue.get("web_url"),
    )


def map_merge_request(raw_mr: dict) -> MergeRequestItem:
    return MergeRequestItem(
        id=raw_mr["id"],
        iid=raw_mr["iid"],
        project_id=raw_mr["project_id"],
        title=raw_mr["title"],
        state=raw_mr["state"],
        created_at=raw_mr["created_at"],
        source_branch=raw_mr["source_branch"],
        target_branch=raw_mr["target_branch"],
        web_url=raw_mr["web_url"],
    )
