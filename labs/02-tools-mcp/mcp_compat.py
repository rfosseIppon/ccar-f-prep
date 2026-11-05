"""Couche de compatibilité du SDK Python `mcp` (fournie).

Le SDK existe en deux versions majeures avec des API différentes :
  - 1.x : `from mcp.server.fastmcp import FastMCP` (celui du cours Anthropic Academy) ;
  - 2.x : FastMCP devient `from mcp.server.mcpserver import MCPServer`, et le client change de forme.

`make_server` renvoie le bon serveur, `Session` donne la même vue des deux clients. Le protocole, lui, est identique :
les résultats d'outil portent le drapeau d'erreur `isError`, quelle que soit la version du SDK.
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

try:  # SDK 1.x
    from mcp.server.fastmcp import FastMCP as _Server

    SDK_MAJOR = 1
except ModuleNotFoundError:  # SDK 2.x
    from mcp.server.mcpserver import MCPServer as _Server  # type: ignore[no-redef]

    SDK_MAJOR = 2

from mcp.types import CallToolResult, TextContent  # noqa: E402


def make_server(name: str) -> Any:
    return _Server(name)


def error_result(payload: dict[str, Any]) -> CallToolResult:
    """Résultat d'outil en erreur : drapeau `isError` levé, charge utile JSON dans le texte."""
    return CallToolResult(isError=True, content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))])


def ok_result(payload: dict[str, Any]) -> CallToolResult:
    """Résultat d'outil réussi (y compris un résultat vide valide)."""
    return CallToolResult(isError=False, content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))])


@dataclass
class ToolInfo:
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class Outcome:
    is_error: bool
    text: str

    def json(self) -> Any:
        return json.loads(self.text)


def _attr(obj: Any, *names: str, default: Any = None) -> Any:
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default


class Session:
    """Vue commune sur le client des deux versions."""

    def __init__(self, raw: Any):
        self._raw = raw

    async def list_tools(self) -> list[ToolInfo]:
        result = await self._raw.list_tools()
        return [ToolInfo(t.name, t.description or "", _attr(t, "inputSchema", "input_schema", default={})) for t in result.tools]

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Outcome:
        result = await self._raw.call_tool(name, arguments or {})
        text = "".join(getattr(c, "text", "") for c in result.content)
        return Outcome(bool(_attr(result, "isError", "is_error", default=False)), text)

    async def list_resources(self) -> list[str]:
        result = await self._raw.list_resources()
        return [str(r.uri) for r in result.resources]

    async def read_resource(self, uri: str) -> str:
        result = await self._raw.read_resource(uri)
        return "".join(getattr(c, "text", "") for c in result.contents)


@asynccontextmanager
async def in_memory_session(server: Any) -> AsyncIterator[Session]:
    """Client relié au serveur dans le même processus : rapide, sans sous-processus."""
    if SDK_MAJOR == 2:
        from mcp.client import Client

        async with Client(server) as client:
            yield Session(client)
    else:
        from mcp.shared.memory import create_connected_server_and_client_session

        async with create_connected_server_and_client_session(server._mcp_server) as client:
            yield Session(client)


@asynccontextmanager
async def stdio_session(command: str, args: list[str], env: dict[str, str] | None = None, cwd: str | None = None) -> AsyncIterator[Session]:
    """Lance le serveur comme Claude Code le ferait (sous-processus, transport stdio)."""
    from mcp import StdioServerParameters

    params = StdioServerParameters(command=command, args=args, env=env, cwd=cwd)
    if SDK_MAJOR == 2:
        from mcp.client import Client

        async with Client(params) as client:
            yield Session(client)
    else:
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                yield Session(client)
