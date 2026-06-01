from fastapi import FastAPI

from app.settings import get_settings


# Validate required environment variables when the application starts.
settings = get_settings()

app = FastAPI(
    title="GitLab Yearly Report Service",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
