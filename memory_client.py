import asyncio
from fastmcp import Client


async def main() -> None:
    # The client starts the server process via stdio.  The command string must
    # point to the Python interpreter that can execute ``memory_server.py``.
    client = Client("python memory_server.py")
    await client.connect()

    try:
        # 1. Save a value in the default namespace.
        saved: bool = await client.call_tool(
            "save_with_namespace",
            {"key": "username", "value": "Алексей", "namespace": "default"},
        )
        print(f"Сохранено: {saved}")

        # 2. Retrieve everything from the default namespace.
        records = await client.call_tool(
            "get_by_namespace",
            {"namespace": "default"},
        )
        print("Данные namespace 'default':")
        for rec in records:
            # ``rec`` is a dict with keys: key, value, timestamp
            print(f"  {rec['key']}: {rec['value']}")

        # 3. Demonstrate wildcard listing.
        keys = await client.call_tool("list_keys", {"pattern": "*name"})
        print(f"Ключи с 'name': {keys}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
