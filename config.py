import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# ---------------------------------------------------------------------------
# LLM configuration
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set")

# Model name – can be overridden via env variable if desired
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ---------------------------------------------------------------------------
# Search configuration
# ---------------------------------------------------------------------------
# The simple DuckDuckGo scraper does not need an API key, but the constant is
# kept for future extensibility.
SEARCH_ENGINE = "duckduckgo"

# ---------------------------------------------------------------------------
# Output configuration
# ---------------------------------------------------------------------------
# All virtual files will be flushed into this directory. It is created on the
# fly if it does not exist.
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
