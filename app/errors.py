import httpx
from fastapi import HTTPException


def raise_for_gitlab_error(response: httpx.Response) -> None:
    if response.status_code < 400:
        return

    if response.status_code == 401:
        raise HTTPException(
            status_code=401,
            detail="GitLab authentication failed",
        )

    if response.status_code == 403:
        raise HTTPException(
            status_code=403,
            detail="GitLab permission denied",
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="GitLab project or resource not found",
        )

    if response.status_code == 429:
        raise HTTPException(
            status_code=429,
            detail="GitLab rate limit exceeded",
        )

    if 500 <= response.status_code <= 599:
        raise HTTPException(
            status_code=502,
            detail="GitLab service error",
        )

    raise HTTPException(
        status_code=502,
        detail="Unexpected GitLab API error",
    )


def raise_for_gitlab_connection_error(error: httpx.RequestError) -> None:
    if isinstance(error, httpx.TimeoutException):
        raise HTTPException(
            status_code=504,
            detail="GitLab request timed out",
        ) from error

    raise HTTPException(
        status_code=502,
        detail="Failed to connect to GitLab",
    ) from error
