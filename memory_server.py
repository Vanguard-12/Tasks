import json
import fnmatch
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List, Dict

from fastmcp import FastMCP


class MemoryServer:
    """MCP server that provides simple key‑value memory with namespace support.

    The data is persisted in a JSON file (``memory_data.json``) with the
    following structure:

    ```json
    {
        "namespace:key": {
            "value": "...",
            "timestamp": "2026-05-15T10:30:00"
        }
    }
    ```
    """

    # FastMCP instance is created as a *class* attribute so that it can be
    # referenced in the decorators below.
    mcp = FastMCP("Memory-Server")

    def __init__(self) -> None:
        self.storage_path = Path("./memory_data.json")

    # ---------------------------------------------------------------------
    # Helper methods for JSON persistence
    # ---------------------------------------------------------------------
    def _load_memory(self) -> Dict[str, Dict[str, Any]]:
        """Load the whole memory dictionary from the JSON file.

        Returns
        -------
        dict
            Mapping ``full_key -> {"value": ..., "timestamp": ...}``.
        """
        if not self.storage_path.exists():
            return {}
        with self.storage_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save_memory(self, data: Dict[str, Dict[str, Any]]) -> None:
        """Write the provided memory dictionary to the JSON file.
        """
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _make_full_key(self, key: str, namespace: str = "default") -> str:
        """Combine namespace and key into the storage key.
        """
        return f"{namespace}:{key}"

    def _validate_key(self, key: str) -> bool:
        """Very small validation – disallow path‑traversal characters.
        """
        # For the purpose of the assignment we simply reject ``/`` and ``..``.
        if "/" in key or ".." in key:
            return False
        return True

    # ---------------------------------------------------------------------
    # MCP tools – CRUD operations
    # ---------------------------------------------------------------------
    @mcp.tool()
    def save(self, key: str, value: Any) -> bool:
        """Save a value under *key*.

        Parameters
        ----------
        key: str
            Identifier for the value (must be unique within the storage).
        value: Any
            JSON‑serialisable value.

        Returns
        -------
        bool
            ``True`` if the value was stored successfully.
        """
        if not self._validate_key(key):
            return False
        data = self._load_memory()
        data[key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._save_memory(data)
        return True

    @mcp.tool()
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a record by *key*.

        Returns a dictionary with ``key``, ``value`` and ``timestamp`` or
        ``None`` when the key does not exist.
        """
        data = self._load_memory()
        record = data.get(key)
        if record is None:
            return None
        return {
            "key": key,
            "value": record.get("value"),
            "timestamp": record.get("timestamp")
        }

    @mcp.tool()
    def delete(self, key: str) -> bool:
        """Delete the entry identified by *key*.

        Returns ``True`` if the key existed and was removed, otherwise ``False``.
        """
        data = self._load_memory()
        if key in data:
            del data[key]
            self._save_memory(data)
            return True
        return False

    @mcp.tool()
    def list_keys(self, pattern: str = "*") -> List[str]:
        """List all stored keys that match a wildcard *pattern*.

        The pattern follows the rules of :mod:`fnmatch` (``*`` and ``?``).
        """
        data = self._load_memory()
        return [k for k in data.keys() if fnmatch.fnmatch(k, pattern)]

    # ---------------------------------------------------------------------
    # Namespace‑aware tools
    # ---------------------------------------------------------------------
    @mcp.tool()
    def save_with_namespace(self, key: str, value: Any, namespace: str = "default") -> bool:
        """Save a value under *key* inside the specified *namespace*.

        The actual storage key is ``"{namespace}:{key}"``.
        """
        if not self._validate_key(key) or not self._validate_key(namespace):
            return False
        full_key = self._make_full_key(key, namespace)
        data = self._load_memory()
        data[full_key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._save_memory(data)
        return True

    @mcp.tool()
    def get_by_namespace(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Return all records that belong to *namespace*.

        Each item in the returned list contains ``key`` (full ``namespace:key``),
        ``value`` and ``timestamp``.
        """
        prefix = f"{namespace}:"
        data = self._load_memory()
        result: List[Dict[str, Any]] = []
        for full_key, record in data.items():
            if full_key.startswith(prefix):
                result.append({
                    "key": full_key,
                    "value": record.get("value"),
                    "timestamp": record.get("timestamp")
                })
        return result


if __name__ == "__main__":
    server = MemoryServer()
    server.mcp.run(
        transport="stdio",
        show_banner=False,
        log_level="ERROR",
    )
