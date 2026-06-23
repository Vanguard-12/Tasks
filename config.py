import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# SerpAPI key for web search
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Agent settings
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.2
