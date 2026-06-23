from langchain_ollama import Ollama
from langchain.agents import create_agent
from langchain.tools import Tool
from tools import search_knowledge_base, add_to_knowledge_base

llm = Ollama(model="llama3", base_url="http://localhost:11434")

tools = [
    Tool.from_function(search_knowledge_base, name="search_knowledge_base", description="Search knowledge base"),
    Tool.from_function(add_to_knowledge_base, name="add_to_knowledge_base", description="Add document to knowledge base"),
]

system_prompt = (
    "You are an assistant that must use the knowledge base to answer questions. "
    "Always search the knowledge base before responding. Use the provided tools."
)

agent = create_agent(llm=llm, tools=tools, system_prompt=system_prompt)
