import os
from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, AgentType, Tool

from tools import search_local_kb, web_search


def create_agent():
    """Create a LangChain agent that can decide between local KB and web search.

    The agent uses the Zero‑Shot ReAct description style. The tool descriptions
    contain hints that guide the LLM to pick the appropriate source.
    """
    # Ensure Ollama server is reachable; the model name can be changed by the user.
    llm = Ollama(model="llama3")

    tools = [
        Tool(
            name="search_local_kb",
            func=search_local_kb,
            description=(
                "Useful when the user asks about information that should be present "
                "in the locally uploaded documents (lecture notes, PDFs, etc.). "
                "Input is a natural language query and an optional integer top_k."
            ),
        ),
        Tool(
            name="web_search",
            func=web_search,
            description=(
                "Useful for up‑to‑date facts, recent news, or any information that may not "
                "be present in the local knowledge base. Input is a natural language query."
            ),
        ),
    ]

    # Zero‑shot ReAct agent that decides which tool to call.
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
    )
    return agent
