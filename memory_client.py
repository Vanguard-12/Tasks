import asyncio
from fastmcp import Client


async def main() -> None:
    # Connect to the MCP server via stdio (the server is started with
    # ``python memory_server.py``).
    client = Client("python memory_server.py")
    await client.connect()

    try:
        # Save a value in the default namespace
        saved = await client.call_tool(
            "save_with_namespace",
            {"key": "username", "value": "Алексей", "namespace": "default"},
        )
        print(f"Сохранено: {saved}")

        # Retrieve all records from the default namespace
        records = await client.call_tool(
            "get_by_namespace",
            {"namespace": "default"},
        )
        print("Данные namespace 'default':")
        for rec in records:
            # ``rec`` contains ``key``, ``value`` and ``timestamp``
            print(f"  {rec['key']}: {rec['value']}")

        # List keys that match a pattern (example: anything ending with 'name')
        keys = await client.call_tool("list_keys", {"pattern": "*name"})
        print(f"Ключи с 'name': {keys}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
