#!/usr/bin/env python3
"""Manage sources in a NotebookLM notebook — list, add, rename, delete.

Usage:
    python3 examples/manage_sources.py <notebook_id>

If no notebook_id is provided, uses the most recently created notebook.
"""

import asyncio
import sys
from notebooklm import NotebookLMClient


async def main():
    async with await NotebookLMClient.from_storage() as client:
        # Get notebook ID from args or use the most recent notebook
        if len(sys.argv) > 1:
            notebook_id = sys.argv[1]
        else:
            notebooks = await client.notebooks.list()
            if not notebooks:
                print("No notebooks found. Create one first with create_notebook.py")
                return
            notebook_id = notebooks[0].id
            print(f"Using notebook: {notebooks[0].title}\n")

        # List existing sources
        sources = await client.sources.list(notebook_id)
        print(f"Current sources ({len(sources)}):")
        for src in sources:
            print(f"  - [{src.kind}] {src.title} (id: {src.id[:12]}...)")

        # Add a new text source
        print("\nAdding a new text source...")
        new_source = await client.sources.add_text(
            notebook_id,
            title="Temporary Note",
            content="This is a temporary source that will be renamed and then deleted.",
            wait=True,
        )
        print(f"Added: {new_source.title} (id: {new_source.id[:12]}...)")

        # Rename the source
        print("\nRenaming source...")
        await client.sources.rename(notebook_id, new_source.id, "Renamed Note")
        print("Renamed to: Renamed Note")

        # Delete the source
        print("\nDeleting source...")
        await client.sources.delete(notebook_id, new_source.id)
        print("Deleted successfully.")

        # Confirm final state
        sources = await client.sources.list(notebook_id)
        print(f"\nFinal sources ({len(sources)}):")
        for src in sources:
            print(f"  - [{src.kind}] {src.title}")


if __name__ == "__main__":
    asyncio.run(main())
