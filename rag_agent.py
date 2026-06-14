from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType, Tool

from rag_tools import search_knowledge_base, add_to_knowledge_base


def get_agent():
    """Create an agent that can call the RAG tools.

    The agent uses Ollama's ``llama3`` model for chat and is configured to
    use the OpenAI‑style function calling interface (``AgentType.OPENAI_FUNCTIONS``).
    """
    llm = ChatOllama(model="llama3")
    tools = [
        Tool.from_function(search_knowledge_base),
        Tool.from_function(add_to_knowledge_base),
    ]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=False,
    )
    return agent
