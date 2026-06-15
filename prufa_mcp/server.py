"""Prufa MCP server — the QA agent for your vibe-coded app.

Apache-2.0. See LICENSE in the repo root.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from prufa_mcp.audit import run_audit, get_report


server = Server("prufa-mcp")


OSS_TOOLS: list[Tool] = [
    Tool(
        name="prufa_run_audit",
        description=(
            "Run a public-page QA audit on a URL. Returns findings JSON: "
            "tracking pixels, broken flows, consent violations, console errors, "
            "compliance signals. Rate-limited; one call returns one audit."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The public URL to audit. Must be authorized for the workspace.",
                },
                "wait": {
                    "type": "boolean",
                    "default": True,
                    "description": "Block until the audit completes (recommended for agents).",
                },
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="prufa_get_report",
        description=(
            "Fetch a shareable report for a completed audit. Returns the report URL "
            "and a summary of findings. Rate-limited."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "report_id": {
                    "type": "string",
                    "description": "The report ID returned by prufa_run_audit.",
                },
            },
            "required": ["report_id"],
        },
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return OSS_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "prufa_run_audit":
        result = await run_audit(
            url=arguments["url"],
            wait=arguments.get("wait", True),
        )
    elif name == "prufa_get_report":
        result = await get_report(report_id=arguments["report_id"])
    else:
        return [TextContent(type="text", text=json.dumps({"error": f"unknown tool: {name}"}))]

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def main() -> None:
    """Sync entrypoint for the console_scripts system.

    Wraps :func:`_amain` in :func:`asyncio.run` so the `prufa-mcp` console
    script (which doesn't await coroutines) works correctly.
    """
    asyncio.run(_amain())


async def _amain() -> None:
    parser = argparse.ArgumentParser(description="Prufa MCP server (OSS)")
    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="Transport. Only stdio is supported in the OSS build.",
    )
    args = parser.parse_args()

    if args.transport != "stdio":
        print("Only stdio transport is supported in the OSS build", file=sys.stderr)
        sys.exit(2)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    main()
