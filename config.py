import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

@dataclass
class Config:
    """Configuration holder for the DeepAgent project.

    All values are read from environment variables with sensible defaults.
    """
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    temperature: float = float(os.getenv("TEMPERATURE", "0.0"))
    output_dir: str = os.getenv("OUTPUT_DIR", "output")

# Export a singleton instance for convenient import elsewhere
config = Config()
