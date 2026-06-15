"""Thin client for Prufa's hosted audit API.

The OSS MCP server is a thin client. Real audit execution, deterministic
checks (BeaconEvent analyzers, consent rules), Playwright orchestration,
and the human-readable report live in the hosted product. This file
proxies audit-trigger and report-fetch calls to that hosted API.
"""
from __future__ import annotations

import os
from typing import Any

import httpx


PRUFA_API_BASE = os.environ.get("PRUFA_API_BASE", "https://app.prufa.dev")
PRUFA_API_TOKEN = os.environ.get("PRUFA_API_TOKEN", "")


async def run_audit(*, url: str, wait: bool = True) -> dict[str, Any]:
    """Trigger a public-page audit on a URL."""
    if not PRUFA_API_TOKEN:
        return {
            "error": "missing_token",
            "hint": "Set PRUFA_API_TOKEN to a Prufa API key. Run `prufa-mcp setup` for a guided flow.",
            "docs": "https://prufa.dev/docs/mcp",
        }

    headers = {"Authorization": f"Bearer {PRUFA_API_TOKEN}", "Idempotency-Key": f"mcp-{url}"}
    timeout = 120.0 if wait else 10.0
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{PRUFA_API_BASE}/api/v1/audits",
            json={"url": url, "wait": wait},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


async def get_report(*, report_id: str) -> dict[str, Any]:
    """Fetch a shareable report for a completed audit."""
    if not PRUFA_API_TOKEN:
        return {
            "error": "missing_token",
            "hint": "Set PRUFA_API_TOKEN to a Prufa API key.",
            "docs": "https://prufa.dev/docs/mcp",
        }

    headers = {"Authorization": f"Bearer {PRUFA_API_TOKEN}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{PRUFA_API_BASE}/api/v1/reports/{report_id}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
