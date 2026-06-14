import sys
from pathlib import Path
from typing import Any, Dict

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.schema import HumanMessage

from config import OPENAI_API_KEY, OPENAI_MODEL, OUTPUT_DIR
from virtual_file_system import VirtualFileSystem
from search_tool import DuckDuckGoSearch

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _search_tool(query: str) -> str:
    """Tool wrapper that performs a DuckDuckGo search.

    The LLM will call this function with a natural‑language query. The function
    returns a concise plain‑text summary of the top results.
    """
    return DuckDuckGoSearch.search(query)


def _write_file_tool(path: str, content: str) -> str:
    """Tool wrapper that writes *content* to a virtual file at *path*.

    The function stores the file in the global ``vfs`` instance.
    """
    global vfs
    vfs.create_file(path, content)
    return f"Virtual file created at '{path}'."


def _finalize_tool() -> str:
    """Special tool that tells the agent we are done.

    It flushes the virtual file system to the real ``output/`` directory and
    returns a short confirmation message.
    """
    global vfs
    vfs.flush_to_disk(OUTPUT_DIR)
    files = "\n".join(vfs.list_files())
    return f"All virtual files have been written to the real output directory.\nCreated files:\n{files}"

# ---------------------------------------------------------------------------
# Build LangChain ``Tool`` objects
# ---------------------------------------------------------------------------
search_tool = Tool(
    name="search",
    func=_search_tool,
    description="Useful for searching the web. Input should be a search query.",
)

write_file_tool = Tool(
    name="write_file",
    func=_write_file_tool,
    description=(
        "Create or overwrite a virtual file. "
        "Input should be a JSON object with two keys: 'path' (relative file path) "
        "and 'content' (the text to write)."
    ),
)

finalize_tool = Tool(
    name="finalize",
    func=_finalize_tool,
    description="Call this tool when you are finished and want to persist all virtual files to disk.",
)

# ---------------------------------------------------------------------------
# Agent execution
# ---------------------------------------------------------------------------

def run_agent(user_query: str) -> str:
    """Run the DeepAgent on *user_query* and return the final LLM response.

    The function creates a fresh ``VirtualFileSystem`` instance, registers the
    three tools (search, write_file, finalize) and executes the ReAct loop via
    LangChain's ``initialize_agent`` helper.
    """
    global vfs
    vfs = VirtualFileSystem()

    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=0.0,
        streaming=False,
    )

    tools = [search_tool, write_file_tool, finalize_tool]
    agent = initialize_agent(
        tools,
        llm,
        agent="zero-shot-react-description",
        verbose=False,
        handle_parsing_errors=True,
    )

    # The agent expects a single string input.
    result = agent.run(user_query)
    return str(result)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"<your query>\"")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    final_output = run_agent(query)
    print("\n=== Agent finished ===\n")
    print(final_output)
    print(f"\nVirtual files have been written to: {OUTPUT_DIR.resolve()}")
