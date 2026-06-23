from langchain import OpenAI
from langchain.agents import create_agent, AgentType
from langchain.prompts import ChatPromptTemplate

from config import OPENAI_API_KEY, LLM_MODEL, TEMPERATURE
from search_tool import SearchTool
from virtual_fs import VirtualFileSystem

# Define the web search tool
search_tool = SearchTool()

# Create a simple prompt that instructs the agent to use the web search tool
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that can search the web.")
])

# Instantiate the LLM
llm = OpenAI(api_key=OPENAI_API_KEY, model=LLM_MODEL, temperature=TEMPERATURE)

# Build the agent using create_agent
agent = create_agent(
    llm=llm,
    tools=[search_tool],
    prompt=prompt,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

# Virtual file system instance
vfs = VirtualFileSystem()


def run_query(query: str) -> None:
    """Run a web search query, store results in virtual FS, and export to disk."""
    # Execute the agent
    result = agent.invoke({"input": query})
    # Store the result in virtual FS
    vfs.write_file("search_results.txt", result["output"])
    # Export to real file system
    vfs.export_to_disk()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python agent.py <search query>")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    run_query(query)
