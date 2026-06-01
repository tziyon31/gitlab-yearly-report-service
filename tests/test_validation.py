import os

os.environ["GITLAB_URL"] = "https://gitlab.example.com"
os.environ["GITLAB_TOKEN"] = "dummy-token"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_issues_missing_year_returns_400():
    response = client.get("/issues")

    assert response.status_code == 400
    assert response.json()["detail"] == "Missing required query parameter: year"


def test_issues_invalid_year_returns_400():
    response = client.get("/issues?year=abc")

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid year format. Expected a 4-digit year, for example 2025"
    )


def test_merge_requests_missing_year_returns_400():
    response = client.get("/merge-requests")

    assert response.status_code == 400
    assert response.json()["detail"] == "Missing required query parameter: year"


def test_merge_requests_invalid_year_returns_400():
    response = client.get("/merge-requests?year=abc")

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid year format. Expected a 4-digit year, for example 2025"
    )
