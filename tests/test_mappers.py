from app.mappers import map_issue, map_merge_request


def test_map_issue():
    raw_issue = {
        "id": 10,
        "iid": 3,
        "project_id": 99,
        "title": "Fix login",
        "state": "opened",
        "created_at": "2025-01-10T12:00:00Z",
        "web_url": "https://gitlab.example.com/group/project/-/issues/3",
    }

    item = map_issue(raw_issue)

    assert item.id == 10
    assert item.iid == 3
    assert item.project_id == 99
    assert item.title == "Fix login"
    assert item.state == "opened"
    assert item.created_at == "2025-01-10T12:00:00Z"
    assert item.web_url == "https://gitlab.example.com/group/project/-/issues/3"


def test_map_merge_request():
    raw_mr = {
        "id": 20,
        "iid": 5,
        "project_id": 99,
        "title": "Add auth",
        "state": "merged",
        "created_at": "2025-02-10T12:00:00Z",
        "source_branch": "feature/auth",
        "target_branch": "main",
        "web_url": "https://gitlab.example.com/group/project/-/merge_requests/5",
    }

    item = map_merge_request(raw_mr)

    assert item.id == 20
    assert item.iid == 5
    assert item.project_id == 99
    assert item.title == "Add auth"
    assert item.state == "merged"
    assert item.created_at == "2025-02-10T12:00:00Z"
    assert item.source_branch == "feature/auth"
    assert item.target_branch == "main"
    assert item.web_url == "https://gitlab.example.com/group/project/-/merge_requests/5"
