# GitLab Yearly Report Service

A small, **read-only** web service that talks to the GitLab REST API v4 and produces
yearly reports of:

- **Issues** created in a specific year
- **Merge requests** created in a specific year

Each report can be scoped to a **single project** or to the **whole GitLab instance**
(bounded by the permissions of the provided token). The service never creates,
updates, or deletes anything in GitLab.

> ### 📌 Don't miss the deep dive
> The most interesting part of this assignment was the **instance-wide `scope=all`**
> edge case. **→ [Press here to jump to the Note](#deep-dive)**

---

## Features

- `GET /health`, `GET /issues`, `GET /merge-requests` HTTP API (FastAPI).
- Year filtering pushed down to GitLab via `created_after` / `created_before` (UTC).
- Full pagination handling (walks every page via the `X-Next-Page` header).
- Project path **or** numeric ID supported (`my-group/my-project` is URL-encoded).
- Precise error mapping (401 / 403 / 404 / 504 / 502) instead of leaking raw upstream errors.
- Configuration only through environment variables; **no secrets baked into the image**.
- Multi-stage, non-root Dockerfile.
- Automated `pytest` suite with unit and endpoint-level tests.

---

## Project structure

```
app/
├── main.py          # FastAPI app + endpoints (HTTP layer)
├── settings.py      # Reads/validates GITLAB_URL and GITLAB_TOKEN from the env
├── gitlab_client.py # Low-level GitLab HTTP: URL building, auth header, timeout, pagination
├── reports.py       # Assignment-level functions: get_issues_by_year / get_merge_requests_by_year
├── year_filters.py  # Year parsing/validation + GitLab date-range params
├── mappers.py       # Raw GitLab JSON -> response schemas
├── schemas.py       # Pydantic response models (the API contract)
└── errors.py        # GitLab status code -> HTTP error mapping
tests/               # pytest suite
Dockerfile
requirements.txt      # runtime dependencies
requirements-dev.txt  # runtime + pytest (not shipped in the image)
```

The layering is deliberate: `gitlab_client.py` only knows *how to talk to GitLab*,
`reports.py` knows *what the assignment asks for*, and `main.py` only does HTTP.
This keeps each piece small and easy to review (and lets a future MCP server reuse
`reports.py` directly).

---

## Configuration

The service is configured entirely through environment variables:

| Variable                 | Required | Default              | Description                                              |
| ------------------------ | -------- | -------------------- | -------------------------------------------------------- |
| `GITLAB_URL`             | Yes      | —                    | Base URL of the GitLab instance, e.g. `https://gitlab.com` |
| `GITLAB_TOKEN`           | Yes      | —                    | Personal/Project access token with **read** permissions  |
| `REQUEST_TIMEOUT_SECONDS`| No       | `30`                 | Read timeout (seconds) for each GitLab call               |

If `GITLAB_URL` or `GITLAB_TOKEN` is missing, the service **fails fast at startup**
with a clear error rather than crashing mid-request.

### Token permissions (read-only)

The token only needs **read** access. The recommended choice is a token scoped to
`read_api` (read-only) — never `api` (which also grants write). A fine-grained
personal access token works too; for the **instance-wide** endpoints GitLab requires
the user-level permissions **`Work Item: Read`** (issues) and **`Merge Request: Read`**.

> The token is provided only at runtime via an environment variable. The Docker
> image contains no secrets. In production the token should be injected by the
> runtime platform (Kubernetes Secrets, Docker secrets, Vault, or a cloud secret
> manager).

---

## Run with Docker

```bash
docker build -t gitlab-yearly-report-service .

docker run --rm -p 8080:8080 \
  -e GITLAB_URL="https://gitlab.com" \
  -e GITLAB_TOKEN="glpat-xxxx" \
  gitlab-yearly-report-service
```

The service is then available at `http://localhost:8080`.

## Run locally (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GITLAB_URL="https://gitlab.com"
export GITLAB_TOKEN="glpat-xxxx"

uvicorn app.main:app --port 8080
```

---

## API

| Endpoint                                        | Description                                        |
| ----------------------------------------------- | -------------------------------------------------- |
| `GET /health`                                   | Returns `{"status": "ok"}`                         |
| `GET /issues?year=2025`                         | Issues from the whole instance (token-scoped)      |
| `GET /issues?year=2025&project=<id-or-path>`    | Issues from a specific project                     |
| `GET /merge-requests?year=2025`                 | Merge requests from the whole instance             |
| `GET /merge-requests?year=2025&project=<id-or-path>` | Merge requests from a specific project        |

`project` accepts either a numeric ID (`77374431`) or a URL-encoded path
(`my-group%2Fmy-project`).

### Example issues response

```json
{
  "year": 2025,
  "project": "tziyon31/Ted-Search",
  "count": 1,
  "items": [
    {
      "id": 10,
      "iid": 3,
      "project_id": 99,
      "title": "Fix login",
      "state": "opened",
      "created_at": "2025-01-10T12:00:00Z",
      "web_url": "https://gitlab.com/.../issues/3"
    }
  ]
}
```

### Example merge requests response

```json
{
  "year": 2025,
  "project": "tziyon31/Ted-Search",
  "count": 1,
  "items": [
    {
      "id": 20,
      "iid": 5,
      "project_id": 99,
      "title": "Add auth",
      "state": "merged",
      "created_at": "2025-02-10T12:00:00Z",
      "source_branch": "feature/auth",
      "target_branch": "main",
      "web_url": "https://gitlab.com/.../merge_requests/5"
    }
  ]
}
```

### Example curl commands

```bash
# Health
curl -i "http://localhost:8080/health"

# Project-scoped (works against any instance, including GitLab.com)
curl -s "http://localhost:8080/issues?year=2025&project=tziyon31%2FTed-Search"
curl -s "http://localhost:8080/merge-requests?year=2025&project=77374431"

# Instance-wide (intended for an appropriately sized instance — see Design note)
curl -s "http://localhost:8080/issues?year=2025"
curl -s "http://localhost:8080/merge-requests?year=2025"
```

The API returns standard (compact) JSON. For readable output, pipe it through `jq`:

```bash
# Pretty-print the full report
curl -s "http://localhost:8080/issues?year=2025&project=77374431" | jq

# Compact one line per item: iid, state, title
curl -s "http://localhost:8080/merge-requests?year=2025&project=77374431" \
  | jq -r '.items[] | "\(.iid)\t\(.state)\t\(.title)"'
```

---

## Error handling

| Scenario                      | HTTP status returned | Body `detail`                          |
| ----------------------------- | -------------------- | -------------------------------------- |
| Missing `year`                | `400`                | `Missing required query parameter: year` |
| Invalid `year` format         | `400`                | `Invalid year format ...`              |
| `GITLAB_TOKEN` missing        | startup failure      | `Missing required environment variables: GITLAB_TOKEN` |
| GitLab authentication failed  | `401`                | `GitLab authentication failed`         |
| GitLab permission denied      | `403`                | `GitLab permission denied`             |
| GitLab project not found      | `404`                | `GitLab project or resource not found` |
| GitLab timeout / upstream 408 | `504`                | `GitLab request timed out`             |
| GitLab rate limit (429)       | `429`                | `GitLab rate limit exceeded`           |
| GitLab 5xx / unreachable      | `502`                | `GitLab service error` / `Failed to connect to GitLab` |

The service maps upstream GitLab errors to accurate HTTP statuses and never forwards
raw GitLab error bodies to the caller.

---

## Tests

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

`pytest` is a development-only dependency (in `requirements-dev.txt`), so it is **not**
installed into the runtime Docker image.

Automated pytest suite with unit and endpoint-level tests. Coverage includes:
`/health`, year validation (400 not 422), URL building and project encoding,
pagination across pages, GitLab error mapping (401/403/404/408/429/5xx), and the
`/issues` & `/merge-requests` endpoints (GitLab calls stubbed).

A smoke test script (`smoke_test.sh`) is included for testing against a running
service and a real GitLab token, including the 400 and 404 cases.

## Verification (local GitLab instance, no jq)

With the service running on `http://localhost:8080`:

```bash
# 1) Health
curl -i "http://localhost:8080/health"

# 2) Issues, instance-wide
curl -i "http://localhost:8080/issues?year=2026"

# 3) Issues, project-scoped
curl -i "http://localhost:8080/issues?year=2026&project=root%2F1"

# 4) Merge requests, instance-wide
curl -i "http://localhost:8080/merge-requests?year=2026"

# 5) Validation error (missing year -> 400)
curl -i "http://localhost:8080/issues"
```

---

<a id="deep-dive"></a>

## Note: the instance-wide (`scope=all`) edge case

The project-scoped endpoints are straightforward and reliable. The interesting part of
this assignment is the **instance-wide** report ("the entire GitLab instance, according
to the permissions of the provided token"). I investigated it carefully, and this
section documents what I found and the reasoning behind the final design.

### The requirement and the first approach

Instance-wide is implemented with GitLab's global endpoints plus `scope=all`
(`GET /issues?scope=all`, `GET /merge_requests?scope=all`). `scope=all` is a
**visibility** scope: "everything the authenticated token can see across the instance".

### What I observed against GitLab.com

Against GitLab.com the global calls consistently failed:

- `GET /issues?scope=all&created_after=...&created_before=...` → GitLab **500 Internal Server Error**
- `GET /merge_requests?scope=all...` → GitLab **408 Request timed out**

while the same query scoped to a single project returned `200 OK` instantly.

### Investigating "is it just too much data?"

1. **Token scope.** I wondered whether a more tightly scoped token would bound the
   result set, so I tried the **fine-grained personal access token (Beta)** restricted
   to my personal projects. The global endpoints still failed — and I confirmed via
   the GitLab error body that they require user-level `Work Item: Read` /
   `Merge Request: Read`. Even after granting those, the global query still returned
   500/408. Conclusion: **no token configuration bounds `scope=all` to my own projects**
   — `scope=all` means "everything visible", which on GitLab.com includes every public
   project.

2. **Narrowing the date window.** To test whether the failure was driven by result
   volume, I shrank the date range. A **one-day** window still returned 500; only a
   **one-minute** window started returning a response. So the cost scales with how much
   data the query must consider.

3. **Pagination (`per_page`).** I then forced `per_page=1`, expecting pagination to let
   GitLab "return a little at a time". It still failed with the same error. This was the
   key insight: **pagination limits how many rows are *returned*, not how much work the
   database must do to produce them.** To return even page 1 ordered by `created_at`,
   GitLab must first evaluate the visibility predicate across the entire accessible
   dataset (all public projects), sort it, and only then apply `LIMIT`. The expensive
   part happens *before* the limit, so it hits a statement timeout regardless of page
   size. Keyset pagination avoids `OFFSET` cost but does not fix this initial cost.

### The alternative I considered: per-project enumeration

The robust pattern (and what GitLab's own UI uses) is to **enumerate the token's
projects** (`GET /projects?membership=true`) and query each project individually
(`GET /projects/:id/issues`), then aggregate. Each call is cheap and bounded, so it
works at any scale. I considered streaming the aggregated results page-by-page, but a
streamed response no longer matches the simple, bounded JSON *report* contract this
service exposes (and the result volume for one user/one year is small enough to return
in a single response anyway).

### Final decision

`scope=all` is the correct, literal interpretation of "the entire instance according to
the token's permissions", and it works exactly as intended against an
**appropriately sized instance** — which is precisely the **local GitLab playground**
the assignment suggests. On a giant public SaaS instance like GitLab.com the global
endpoint is impractical (GitLab itself times out), so this service is intended to be
validated instance-wide against a dedicated/self-hosted instance, while project-scoped
reports work everywhere including GitLab.com.

The service maps GitLab's `500 → 502` and `408 → 504` so that, even in this edge case,
the failure is reported accurately instead of hanging or returning a misleading 500.

### Possible future improvements

- **Per-project (or per-group) enumeration** for reliable instance-wide reports on very
  large instances.
- **Bounded concurrency** across projects to speed up enumeration.
- **GraphQL** to fetch projects + their issues/MRs in fewer round-trips.
- **Streaming / cursor pagination** of the service's own responses if result volume ever
  becomes large.

---

## Local GitLab playground (optional)

To validate instance-wide reporting against a small, dedicated instance:

```bash
export GITLAB_HOME=/tmp/gitlab
sudo docker run --detach \
  --hostname gitlab.example.com \
  --env GITLAB_OMNIBUS_CONFIG="external_url 'http://gitlab.example.com'" \
  --publish 443:443 --publish 80:80 --publish 22:22 \
  --name gitlab --restart always \
  --volume $GITLAB_HOME/config:/etc/gitlab \
  --volume $GITLAB_HOME/logs:/var/log/gitlab \
  --volume $GITLAB_HOME/data:/var/opt/gitlab \
  --shm-size 256m \
  gitlab/gitlab-ee:18.10.5-ee.0
```

After GitLab starts, create groups, projects, issues, and merge requests, create a
read-scoped token, and point the service at it via `GITLAB_URL` / `GITLAB_TOKEN`.
```
