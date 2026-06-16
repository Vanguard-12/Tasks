import os
import yaml
from typing import List

from langchain.agents import initialize_agent, AgentType, Tool
from langchain.llms import Ollama
from langchain.prompts import ChatPromptTemplate

# Import the tools defined in rag_tools.py
from rag_tools import add_to_knowledge_base, search_knowledge_base

# Load configuration (optional – allows overriding the LLM model)
CONFIG_PATH = os.getenv("RAG_CONFIG", "config.yaml")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    llm_model = cfg.get("ollama", {}).get("llm_model", "llama3")
else:
    llm_model = "llama3"


def get_agent() -> "Agent":
    """Create and return a LangChain chat agent equipped with RAG tools."""
    llm = Ollama(model=llm_model)
    tools: List[Tool] = [Tool.from_function(add_to_knowledge_base), Tool.from_function(search_knowledge_base)]

    system_prompt = (
        "You are an AI assistant with access to a knowledge base. "
        "When you need factual information, use the provided tools. "
        "Use `search_knowledge_base` to retrieve relevant chunks and incorporate them into your answer. "
        "If you need to store new information, call `add_to_knowledge_base`."
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        prompt=prompt,
        verbose=False,
    )
    return agent


if __name__ == "__main__":
    agent = get_agent()
    print("RAG Agent ready. Type 'quit' or 'exit' to stop.")
    while True:
        user_input = input("User: ")
        if user_input.lower() in {"quit", "exit"}:
            break
        response = agent.run(user_input)
        print("Agent:", response)
