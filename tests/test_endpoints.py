import os

os.environ["GITLAB_URL"] = "https://gitlab.example.com"
os.environ["GITLAB_TOKEN"] = "dummy-token"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_issues_endpoint_without_project_maps_gitlab_response(monkeypatch):
    captured = {}

    def fake_get_paginated_from_gitlab(settings, path, params):
        captured["path"] = path
        captured["params"] = params

        return [
            {
                "id": 10,
                "iid": 3,
                "project_id": 99,
                "title": "Fix login",
                "state": "opened",
                "created_at": "2025-01-10T12:00:00Z",
                "web_url": "https://gitlab.example.com/group/project/-/issues/3",
            }
        ]

    monkeypatch.setattr(
        "app.reports.get_paginated_from_gitlab",
        fake_get_paginated_from_gitlab,
    )

    response = client.get("/issues?year=2025")

    assert response.status_code == 200

    assert captured["path"] == "/issues"
    assert captured["params"] == {
        "created_after": "2025-01-01T00:00:00Z",
        "created_before": "2026-01-01T00:00:00Z",
        "scope": "all",
        "per_page": 100,
    }

    assert response.json() == {
        "year": 2025,
        "project": None,
        "count": 1,
        "items": [
            {
                "id": 10,
                "iid": 3,
                "project_id": 99,
                "title": "Fix login",
                "state": "opened",
                "created_at": "2025-01-10T12:00:00Z",
                "web_url": "https://gitlab.example.com/group/project/-/issues/3",
            }
        ],
    }


def test_issues_endpoint_with_project_maps_gitlab_response(monkeypatch):
    captured = {}

    def fake_get_paginated_from_gitlab(settings, path, params):
        captured["path"] = path
        captured["params"] = params

        return [
            {
                "id": 11,
                "iid": 4,
                "project_id": 100,
                "title": "Fix permissions",
                "state": "closed",
                "created_at": "2025-02-10T12:00:00Z",
                "web_url": "https://gitlab.example.com/my-group/my-project/-/issues/4",
            }
        ]

    monkeypatch.setattr(
        "app.reports.get_paginated_from_gitlab",
        fake_get_paginated_from_gitlab,
    )

    response = client.get("/issues?year=2025&project=my-group/my-project")

    assert response.status_code == 200

    assert captured["path"] == "/projects/my-group%2Fmy-project/issues"
    assert captured["params"] == {
        "created_after": "2025-01-01T00:00:00Z",
        "created_before": "2026-01-01T00:00:00Z",
        "scope": "all",
        "per_page": 100,
    }

    assert response.json() == {
        "year": 2025,
        "project": "my-group/my-project",
        "count": 1,
        "items": [
            {
                "id": 11,
                "iid": 4,
                "project_id": 100,
                "title": "Fix permissions",
                "state": "closed",
                "created_at": "2025-02-10T12:00:00Z",
                "web_url": "https://gitlab.example.com/my-group/my-project/-/issues/4",
            }
        ],
    }


def test_merge_requests_endpoint_without_project_maps_gitlab_response(monkeypatch):
    captured = {}

    def fake_get_paginated_from_gitlab(settings, path, params):
        captured["path"] = path
        captured["params"] = params

        return [
            {
                "id": 20,
                "iid": 5,
                "project_id": 99,
                "title": "Add auth",
                "state": "merged",
                "created_at": "2025-03-10T12:00:00Z",
                "source_branch": "feature/auth",
                "target_branch": "main",
                "web_url": "https://gitlab.example.com/group/project/-/merge_requests/5",
            }
        ]

    monkeypatch.setattr(
        "app.reports.get_paginated_from_gitlab",
        fake_get_paginated_from_gitlab,
    )

    response = client.get("/merge-requests?year=2025")

    assert response.status_code == 200

    assert captured["path"] == "/merge_requests"
    assert captured["params"] == {
        "created_after": "2025-01-01T00:00:00Z",
        "created_before": "2026-01-01T00:00:00Z",
        "scope": "all",
        "per_page": 100,
    }

    assert response.json() == {
        "year": 2025,
        "project": None,
        "count": 1,
        "items": [
            {
                "id": 20,
                "iid": 5,
                "project_id": 99,
                "title": "Add auth",
                "state": "merged",
                "created_at": "2025-03-10T12:00:00Z",
                "source_branch": "feature/auth",
                "target_branch": "main",
                "web_url": "https://gitlab.example.com/group/project/-/merge_requests/5",
            }
        ],
    }


def test_merge_requests_endpoint_with_project_maps_gitlab_response(monkeypatch):
    captured = {}

    def fake_get_paginated_from_gitlab(settings, path, params):
        captured["path"] = path
        captured["params"] = params

        return [
            {
                "id": 21,
                "iid": 6,
                "project_id": 100,
                "title": "Improve CI",
                "state": "opened",
                "created_at": "2025-04-10T12:00:00Z",
                "source_branch": "feature/ci",
                "target_branch": "main",
                "web_url": "https://gitlab.example.com/my-group/my-project/-/merge_requests/6",
            }
        ]

    monkeypatch.setattr(
        "app.reports.get_paginated_from_gitlab",
        fake_get_paginated_from_gitlab,
    )

    response = client.get(
        "/merge-requests?year=2025&project=my-group/my-project"
    )

    assert response.status_code == 200

    assert captured["path"] == "/projects/my-group%2Fmy-project/merge_requests"
    assert captured["params"] == {
        "created_after": "2025-01-01T00:00:00Z",
        "created_before": "2026-01-01T00:00:00Z",
        "scope": "all",
        "per_page": 100,
    }

    assert response.json() == {
        "year": 2025,
        "project": "my-group/my-project",
        "count": 1,
        "items": [
            {
                "id": 21,
                "iid": 6,
                "project_id": 100,
                "title": "Improve CI",
                "state": "opened",
                "created_at": "2025-04-10T12:00:00Z",
                "source_branch": "feature/ci",
                "target_branch": "main",
                "web_url": "https://gitlab.example.com/my-group/my-project/-/merge_requests/6",
            }
        ],
    }
