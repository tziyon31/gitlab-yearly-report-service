import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    gitlab_url: str
    gitlab_token: str
    enable_membership_fallback: bool = False


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    gitlab_url = os.environ.get("GITLAB_URL")
    gitlab_token = os.environ.get("GITLAB_TOKEN")
    enable_membership_fallback = _env_flag(
        "ENABLE_MEMBERSHIP_FALLBACK",
        default=False,
    )

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
        enable_membership_fallback=enable_membership_fallback,
    )
