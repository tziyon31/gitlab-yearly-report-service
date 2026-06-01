from app.gitlab_client import build_api_url, encode_project_id_or_path
from app.settings import Settings


def test_build_api_url_adds_api_v4_prefix():
    settings = Settings(
        gitlab_url="https://gitlab.example.com",
        gitlab_token="dummy-token",
    )

    result = build_api_url(settings, "/issues")

    assert result == "https://gitlab.example.com/api/v4/issues"


def test_build_api_url_handles_trailing_slash_in_base_url():
    settings = Settings(
        gitlab_url="https://gitlab.example.com/",
        gitlab_token="dummy-token",
    )

    result = build_api_url(settings, "/merge_requests")

    assert result == "https://gitlab.example.com/api/v4/merge_requests"


def test_encode_project_id_keeps_numeric_id_unchanged():
    result = encode_project_id_or_path("123")

    assert result == "123"


def test_encode_project_path_encodes_slashes():
    result = encode_project_id_or_path("my-group/my-project")

    assert result == "my-group%2Fmy-project"


from fastapi import HTTPException

from app.gitlab_client import get_paginated_from_gitlab


class FakeGitLabResponse:
    def __init__(self, payload, headers=None):
        self.payload = payload
        self.headers = headers or {}

    def json(self):
        return self.payload


def test_get_paginated_from_gitlab_collects_all_pages(monkeypatch):
    calls = []

    def fake_get_from_gitlab(settings, path, params):
        calls.append(
            {
                "path": path,
                "params": params,
            }
        )

        if params["page"] == 1:
            return FakeGitLabResponse(
                payload=[{"id": 1}],
                headers={"X-Next-Page": "2"},
            )

        return FakeGitLabResponse(
            payload=[{"id": 2}],
            headers={"X-Next-Page": ""},
        )

    monkeypatch.setattr(
        "app.gitlab_client.get_from_gitlab",
        fake_get_from_gitlab,
    )

    result = get_paginated_from_gitlab(
        settings=None,
        path="/issues",
        params={"per_page": 100},
    )

    assert result == [{"id": 1}, {"id": 2}]
    assert calls == [
        {
            "path": "/issues",
            "params": {"per_page": 100, "page": 1},
        },
        {
            "path": "/issues",
            "params": {"per_page": 100, "page": 2},
        },
    ]


def test_get_paginated_from_gitlab_does_not_mutate_original_params(monkeypatch):
    original_params = {"per_page": 100}

    def fake_get_from_gitlab(settings, path, params):
        return FakeGitLabResponse(
            payload=[{"id": 1}],
            headers={"X-Next-Page": ""},
        )

    monkeypatch.setattr(
        "app.gitlab_client.get_from_gitlab",
        fake_get_from_gitlab,
    )

    get_paginated_from_gitlab(
        settings=None,
        path="/issues",
        params=original_params,
    )

    assert original_params == {"per_page": 100}


def test_get_paginated_from_gitlab_rejects_non_list_response(monkeypatch):
    def fake_get_from_gitlab(settings, path, params):
        return FakeGitLabResponse(
            payload={"message": "unexpected"},
            headers={"X-Next-Page": ""},
        )

    monkeypatch.setattr(
        "app.gitlab_client.get_from_gitlab",
        fake_get_from_gitlab,
    )

    try:
        get_paginated_from_gitlab(
            settings=None,
            path="/issues",
            params={"per_page": 100},
        )
    except HTTPException as error:
        assert error.status_code == 502
        assert error.detail == "Unexpected GitLab response format"
    else:
        raise AssertionError("Expected HTTPException")
