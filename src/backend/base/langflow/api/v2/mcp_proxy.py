"""MCP Proxy Service - Fetches MCP server configurations from Agent Platform."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

from langflow.logging import logger

AGENT_PLATFORM_API_URL_ENV = "AGENT_PLATFORM_API_URL"


def get_agent_platform_url() -> str | None:
    """Get the Agent Platform API URL from environment variable."""
    url = os.environ.get(AGENT_PLATFORM_API_URL_ENV, "").strip()
    return url if url else None


async def fetch_mcp_servers_from_agent_platform() -> dict[str, Any]:
    """Fetch MCP server configurations from the Agent Platform API.

    Returns:
        dict with 'mcpServers' key containing server configurations.
        Returns empty dict if Agent Platform is not configured or unavailable.
    """
    base_url = get_agent_platform_url()
    if not base_url:
        logger.debug("[MCPProxy] AGENT_PLATFORM_API_URL not configured")
        return {"mcpServers": {}}

    url = f"{base_url.rstrip('/')}/mcp/servers"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # Transform to Langflow format
            servers = data.get("mcpServers", {})
            result = {}
            for name, config in servers.items():
                result[name] = {
                    "command": config.get("command", ""),
                    "args": config.get("args", []),
                    "env": config.get("env", {}),
                    "url": config.get("url", ""),
                    "description": config.get("description", ""),
                    "transport": config.get("transport", ""),
                    "is_active": config.get("is_active", True),
                    "source": "agent_platform",
                }

            logger.info("[MCPProxy] Fetched {} MCP servers from Agent Platform", len(result))
            return {"mcpServers": result}

    except httpx.TimeoutException:
        logger.warning("[MCPProxy] Timeout fetching MCP servers from {}", url)
        return {"mcpServers": {}}
    except httpx.HTTPStatusError as e:
        logger.warning("[MCPProxy] HTTP error fetching MCP servers: {}", e)
        return {"mcpServers": {}}
    except (httpx.RequestError, json.JSONDecodeError) as e:
        logger.warning("[MCPProxy] Failed to fetch MCP servers: {}", e)
        return {"mcpServers": {}}


async def fetch_mcp_server_tools_from_agent_platform(server_name: str) -> list[dict[str, Any]]:
    """Fetch available tools for a specific MCP server from Agent Platform.

    Args:
        server_name: Name of the MCP server to query.

    Returns:
        List of tool definitions.
    """
    base_url = get_agent_platform_url()
    if not base_url:
        return []

    url = f"{base_url.rstrip('/')}/mcp/servers/{server_name}/tools"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json().get("tools", [])
    except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError) as e:
        logger.warning("[MCPProxy] Failed to fetch tools for server {}: {}", server_name, e)
        return []
