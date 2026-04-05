#!/usr/bin/env python3
"""List all NotebookLM notebooks with details."""

import asyncio
from notebooklm import NotebookLMClient


async def main():
    async with await NotebookLMClient.from_storage() as client:
        notebooks = await client.notebooks.list()

        if not notebooks:
            print("No notebooks found.")
            return

        print(f"Found {len(notebooks)} notebooks:\n")
        for nb in notebooks:
            created = nb.created_at.strftime("%Y-%m-%d") if nb.created_at else "unknown"
            owner = "you" if nb.is_owner else "shared"
            print(f"  {nb.title}")
            print(f"    ID:      {nb.id}")
            print(f"    Sources: {nb.sources_count}")
            print(f"    Created: {created}")
            print(f"    Owner:   {owner}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
