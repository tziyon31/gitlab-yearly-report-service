import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    gitlab_url: str
    gitlab_token: str


def get_settings() -> Settings:
    gitlab_url = os.environ.get("GITLAB_URL")
    gitlab_token = os.environ.get("GITLAB_TOKEN")

    missing_vars = []

    if not gitlab_url:
        missing_vars.append("GITLAB_URL")

    if not gitlab_token:
        missing_vars.append("GITLAB_TOKEN")

    if missing_vars:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return Settings(
        gitlab_url=gitlab_url.rstrip("/"),
        gitlab_token=gitlab_token,
    )
