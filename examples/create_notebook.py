#!/usr/bin/env python3
"""Create a notebook and add sources (text and URL)."""

import asyncio
from notebooklm import NotebookLMClient


async def main():
    async with await NotebookLMClient.from_storage() as client:
        # Create a new notebook
        notebook = await client.notebooks.create("Claude Code Demo")
        print(f"Created notebook: {notebook.title} ({notebook.id})")

        # Add a text source
        text_source = await client.sources.add_text(
            notebook.id,
            title="Quick Facts",
            content=(
                "Python was created by Guido van Rossum and first released in 1991. "
                "It emphasises code readability and supports multiple programming "
                "paradigms including procedural, object-oriented, and functional."
            ),
            wait=True,
        )
        print(f"Added text source: {text_source.title} (status: {text_source.status})")

        # Add a URL source
        url_source = await client.sources.add_url(
            notebook.id,
            url="https://en.wikipedia.org/wiki/Python_(programming_language)",
            wait=True,
        )
        print(f"Added URL source: {url_source.title} (status: {url_source.status})")

        # List sources to confirm
        sources = await client.sources.list(notebook.id)
        print(f"\nNotebook now has {len(sources)} sources:")
        for src in sources:
            print(f"  - {src.title} ({src.kind})")

        print(f"\nNotebook ID for use in other scripts: {notebook.id}")


if __name__ == "__main__":
    asyncio.run(main())
