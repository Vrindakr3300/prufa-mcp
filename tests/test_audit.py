"""Smoke test: the server returns a clear missing_token error without a token."""
from __future__ import annotations

import asyncio

import pytest

from prufa_mcp.audit import get_report, run_audit


def test_run_audit_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without PRUFA_API_TOKEN, run_audit returns a clear missing_token error."""
    monkeypatch.delenv("PRUFA_API_TOKEN", raising=False)
    result = asyncio.run(run_audit(url="https://example.com", wait=False))
    assert result["error"] == "missing_token", f"Expected missing_token, got {result}"
    assert "PRUFA_API_TOKEN" in result["hint"], "Hint should mention the env var"


def test_get_report_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without PRUFA_API_TOKEN, get_report returns a clear missing_token error."""
    monkeypatch.delenv("PRUFA_API_TOKEN", raising=False)
    result = asyncio.run(get_report(report_id="rep_test123"))
    assert result["error"] == "missing_token", f"Expected missing_token, got {result}"
    assert "PRUFA_API_TOKEN" in result["hint"], "Hint should mention the env var"
