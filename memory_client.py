import asyncio
from fastmcp import Client


async def main() -> None:
    # Connect to the MCP server via stdio (the server is launched as a subprocess)
    client = Client("python memory_server.py")
    await client.connect()

    try:
        # Save a value in the default namespace
        saved = await client.call_tool(
            "save_with_namespace",
            {"key": "username", "value": "Алексей", "namespace": "default"},
        )
        print(f"Сохранено: {saved}")

        # Retrieve all entries from the default namespace
        entries = await client.call_tool(
            "get_by_namespace",
            {"namespace": "default"},
        )
        print("Данные namespace 'default':")
        for item in entries:
            print(f"  {item['key']}: {item['value']}")

        # List keys that match a simple pattern
        keys = await client.call_tool("list_keys", {"pattern": "*name"})
        print(f"Ключи с 'name': {keys}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
