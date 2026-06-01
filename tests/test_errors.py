from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException

from app.errors import (
    raise_for_gitlab_connection_error,
    raise_for_gitlab_error,
)


def make_response(status_code: int):
    return SimpleNamespace(status_code=status_code)


def assert_gitlab_error(
    gitlab_status_code: int,
    expected_status_code: int,
    expected_detail: str,
):
    response = make_response(gitlab_status_code)

    with pytest.raises(HTTPException) as exc_info:
        raise_for_gitlab_error(response)

    assert exc_info.value.status_code == expected_status_code
    assert exc_info.value.detail == expected_detail


def test_raise_for_gitlab_error_does_nothing_for_success_response():
    response = make_response(200)

    assert raise_for_gitlab_error(response) is None


def test_raise_for_gitlab_error_maps_401():
    assert_gitlab_error(
        gitlab_status_code=401,
        expected_status_code=401,
        expected_detail="GitLab authentication failed",
    )


def test_raise_for_gitlab_error_maps_403():
    assert_gitlab_error(
        gitlab_status_code=403,
        expected_status_code=403,
        expected_detail="GitLab permission denied",
    )


def test_raise_for_gitlab_error_maps_404():
    assert_gitlab_error(
        gitlab_status_code=404,
        expected_status_code=404,
        expected_detail="GitLab project or resource not found",
    )


def test_raise_for_gitlab_error_maps_408_to_504():
    assert_gitlab_error(
        gitlab_status_code=408,
        expected_status_code=504,
        expected_detail="GitLab request timed out",
    )


def test_raise_for_gitlab_error_maps_429():
    assert_gitlab_error(
        gitlab_status_code=429,
        expected_status_code=429,
        expected_detail="GitLab rate limit exceeded",
    )


def test_raise_for_gitlab_error_maps_gitlab_5xx_to_502():
    assert_gitlab_error(
        gitlab_status_code=500,
        expected_status_code=502,
        expected_detail="GitLab service error",
    )


def test_raise_for_gitlab_error_maps_unexpected_gitlab_error_to_502():
    assert_gitlab_error(
        gitlab_status_code=418,
        expected_status_code=502,
        expected_detail="Unexpected GitLab API error",
    )


def test_raise_for_gitlab_connection_error_maps_to_502():
    original_error = httpx.RequestError("Connection failed")

    with pytest.raises(HTTPException) as exc_info:
        raise_for_gitlab_connection_error(original_error)

    assert exc_info.value.status_code == 502
    assert exc_info.value.detail == "Failed to connect to GitLab"


def test_raise_for_gitlab_connection_error_maps_timeout_to_504():
    original_error = httpx.ReadTimeout("The read operation timed out")

    with pytest.raises(HTTPException) as exc_info:
        raise_for_gitlab_connection_error(original_error)

    assert exc_info.value.status_code == 504
    assert exc_info.value.detail == "GitLab request timed out"
