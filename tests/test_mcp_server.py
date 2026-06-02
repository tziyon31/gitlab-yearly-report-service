import asyncio
import json
import os

os.environ["GITLAB_URL"] = "https://gitlab.example.com"
os.environ["GITLAB_TOKEN"] = "dummy-token"

from app.schemas import IssuesReport
from gitlab_mcp import server as mcp_server_module


def test_mcp_server_registers_required_tools():
    tools = asyncio.run(mcp_server_module.mcp.list_tools())
    tool_names = {tool.name for tool in tools}

    assert tool_names == {
        "get_issues_by_year",
        "get_merge_requests_by_year",
    }


def test_get_issues_by_year_tool_returns_report_json(monkeypatch):
    def fake_handle(settings, tool_input):
        assert tool_input.year == 2025
        assert tool_input.project_id_or_path == "my-group/my-project"
        return IssuesReport(
            year=2025,
            project="my-group/my-project",
            count=0,
            items=[],
        )

    monkeypatch.setattr(mcp_server_module, "handle_get_issues_by_year", fake_handle)

    content, structured = asyncio.run(
        mcp_server_module.mcp.call_tool(
            "get_issues_by_year",
            {"year": 2025, "project_id_or_path": "my-group/my-project"},
        )
    )

    assert structured is not None
    payload = structured
    assert json.loads(content[0].text) == payload
    assert payload == {
        "year": 2025,
        "project": "my-group/my-project",
        "count": 0,
        "items": [],
    }
