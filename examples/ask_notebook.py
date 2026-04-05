#!/usr/bin/env python3
"""Ask questions to a NotebookLM notebook and handle follow-ups.

Usage:
    python3 examples/ask_notebook.py <notebook_id>

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

        # Ask a question
        result = await client.chat.ask(notebook_id, "What is this notebook about?")
        print(f"Q: What is this notebook about?")
        print(f"A: {result.answer}\n")

        # Follow-up question using the same conversation
        result = await client.chat.ask(
            notebook_id,
            "Give me three key takeaways.",
            conversation_id=result.conversation_id,
        )
        print(f"Q: Give me three key takeaways.")
        print(f"A: {result.answer}\n")


if __name__ == "__main__":
    asyncio.run(main())
