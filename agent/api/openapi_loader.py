from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx


class OpenAPILoadError(RuntimeError):
    pass


async def load_openapi_schema(
    *,
    swagger_url: str | None,
    swagger_file_path: Path | None,
    timeout: float,
) -> tuple[dict[str, Any], str]:
    if swagger_url:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(swagger_url)
            response.raise_for_status()
            return response.json(), f"url:{swagger_url}"

    if not swagger_file_path:
        raise OpenAPILoadError("Set SWAGGER_URL or SWAGGER_FILE_PATH.")

    path = swagger_file_path.expanduser().resolve()
    if not path.exists():
        raise OpenAPILoadError(f"Swagger file does not exist: {path}")

    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), f"file:{path}"
    except json.JSONDecodeError as exc:
        raise OpenAPILoadError(f"Swagger file is not valid JSON: {path}") from exc


def default_base_url_from_schema(schema: dict[str, Any]) -> str | None:
    servers = schema.get("servers")
    if not isinstance(servers, list):
        return None
    for server in servers:
        if isinstance(server, dict) and isinstance(server.get("url"), str):
            return server["url"].rstrip("/")
    return None


def require_paths(schema: dict[str, Any], required_paths: list[str]) -> list[str]:
    paths = schema.get("paths")
    if not isinstance(paths, dict):
        return required_paths
    return [path for path in required_paths if path not in paths]

