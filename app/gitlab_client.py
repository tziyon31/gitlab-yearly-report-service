from urllib.parse import quote

import httpx

from app.errors import raise_for_gitlab_connection_error, raise_for_gitlab_error
from app.settings import Settings


API_PREFIX = "/api/v4"
TIMEOUT_SECONDS = 10.0


def build_api_url(settings: Settings, path: str) -> str:
    base_url = settings.gitlab_url.rstrip("/")
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url}{API_PREFIX}{normalized_path}"


def build_auth_headers(settings: Settings) -> dict[str, str]:
    return {
        "PRIVATE-TOKEN": settings.gitlab_token,
        "Accept": "application/json",
    }


def encode_project_id_or_path(project_id_or_path: str) -> str:
    if project_id_or_path.isdigit():
        return project_id_or_path

    return quote(project_id_or_path, safe="")


def get_from_gitlab(
    settings: Settings,
    path: str,
    params: dict | None = None,
) -> httpx.Response:
    url = build_api_url(settings, path)

    try:
        response = httpx.get(
            url,
            headers=build_auth_headers(settings),
            params=params,
            timeout=TIMEOUT_SECONDS,
        )
    except httpx.RequestError as error:
        raise_for_gitlab_connection_error(error)

    raise_for_gitlab_error(response)

    return response
