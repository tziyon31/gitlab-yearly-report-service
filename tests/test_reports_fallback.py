from fastapi import HTTPException

from app.reports import get_issues_by_year, get_merge_requests_by_year
from app.settings import Settings


def _settings(enable_membership_fallback: bool = False) -> Settings:
    return Settings(
        gitlab_url="https://gitlab.example.com",
        gitlab_token="dummy-token",
        enable_membership_fallback=enable_membership_fallback,
    )


def test_issues_scope_all_falls_back_to_membership_enumeration(monkeypatch):
    calls = []

    def fake_get_paginated_from_gitlab(settings, path, params):
        calls.append(path)
        if path == "/issues":
            raise HTTPException(status_code=504, detail="GitLab request timed out")
        raise AssertionError("Unexpected path in direct flow")

    def fake_fetch_by_membership_enumeration(settings, resource, params):
        assert resource == "issues"
        return [{"id": 101}]

    monkeypatch.setattr(
        "app.reports.get_paginated_from_gitlab",
        fake_get_paginated_from_gitlab,
    )
    monkeypatch.setattr(
        "app.reports.fetch_by_membership_enumeration",
        fake_fetch_by_membership_enumeration,
    )

    result = get_issues_by_year(
        settings=_settings(enable_membership_fallback=True),
        year=2025,
    )

    assert calls == ["/issues"]
    assert result == [{"id": 101}]


def test_merge_requests_scope_all_falls_back_to_membership_enumeration(monkeypatch):
    calls = []

    def fake_get_paginated_from_gitlab(settings, path, params):
        calls.append(path)
        if path == "/merge_requests":
            raise HTTPException(status_code=502, detail="GitLab service error")
        raise AssertionError("Unexpected path in direct flow")

    def fake_fetch_by_membership_enumeration(settings, resource, params):
        assert resource == "merge_requests"
        return [{"id": 202}]

    monkeypatch.setattr(
        "app.reports.get_paginated_from_gitlab",
        fake_get_paginated_from_gitlab,
    )
    monkeypatch.setattr(
        "app.reports.fetch_by_membership_enumeration",
        fake_fetch_by_membership_enumeration,
    )

    result = get_merge_requests_by_year(
        settings=_settings(enable_membership_fallback=True),
        year=2025,
    )

    assert calls == ["/merge_requests"]
    assert result == [{"id": 202}]


def test_scope_all_without_fallback_flag_returns_error_with_hint(monkeypatch):
    fallback_used = {"value": False}

    def fake_get_paginated_from_gitlab(settings, path, params):
        if path == "/issues":
            raise HTTPException(status_code=504, detail="GitLab request timed out")
        raise AssertionError("Unexpected path in direct flow")

    def fake_fetch_by_membership_enumeration(settings, resource, params):
        fallback_used["value"] = True
        return []

    monkeypatch.setattr(
        "app.reports.get_paginated_from_gitlab",
        fake_get_paginated_from_gitlab,
    )
    monkeypatch.setattr(
        "app.reports.fetch_by_membership_enumeration",
        fake_fetch_by_membership_enumeration,
    )

    try:
        get_issues_by_year(
            settings=_settings(enable_membership_fallback=False),
            year=2025,
        )
    except HTTPException as error:
        assert error.status_code == 504
        assert "ENABLE_MEMBERSHIP_FALLBACK=true" in error.detail
        assert "fallback enumeration over membership=true projects" in error.detail
    else:
        raise AssertionError("Expected HTTPException")

    assert fallback_used["value"] is False


def test_project_scoped_request_does_not_use_fallback(monkeypatch):
    fallback_used = {"value": False}

    def fake_get_paginated_from_gitlab(settings, path, params):
        raise HTTPException(status_code=504, detail="GitLab request timed out")

    def fake_fetch_by_membership_enumeration(settings, resource, params):
        fallback_used["value"] = True
        return []

    monkeypatch.setattr(
        "app.reports.get_paginated_from_gitlab",
        fake_get_paginated_from_gitlab,
    )
    monkeypatch.setattr(
        "app.reports.fetch_by_membership_enumeration",
        fake_fetch_by_membership_enumeration,
    )

    try:
        get_issues_by_year(
            settings=_settings(),
            year=2025,
            project_id_or_path="my-group/my-project",
        )
    except HTTPException as error:
        assert error.status_code == 504
    else:
        raise AssertionError("Expected HTTPException")

    assert fallback_used["value"] is False
