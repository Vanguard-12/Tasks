import os
from typing import Callable, Any

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from models import PersonInfo, MeetingNotes
from prompt_templates import BASE_PROMPT
from utils import summarize

# Load environment variables (e.g., OPENAI_API_KEY) if present.
load_dotenv()

# Initialize LLM – defaults to OpenAI Chat model. Users can switch to Ollama by setting
# an environment variable LLM_PROVIDER=ollama and providing OLLAMA_BASE_URL.
def get_llm():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "ollama":
        # Ollama uses the same ChatOpenAI interface with a custom base URL.
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        return ChatOpenAI(base_url=base_url, model="llama3.1:8b", temperature=0)
    # Default: OpenAI
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


class SchemaRouter:
    """Detects which schema (PersonInfo or MeetingNotes) applies to the input text.

    The detection uses a simple keyword heuristic to avoid extra LLM calls, keeping the
    process a single pass.
    """

    PERSON_KEYWORDS = ["имя", "возраст", "профессия", "навыки", "работа", "разработчик"]
    MEETING_KEYWORDS = ["встреча", "участники", "тема", "решение", "дата", "протокол"]

    @staticmethod
    def detect_schema(text: str) -> Callable[[str], Any]:
        lowered = text.lower()
        person_score = sum(kw in lowered for kw in SchemaRouter.PERSON_KEYWORDS)
        meeting_score = sum(kw in lowered for kw in SchemaRouter.MEETING_KEYWORDS)
        # Prefer meeting if its score is higher, otherwise person.
        if meeting_score > person_score:
            return MeetingNotes
        return PersonInfo

    @staticmethod
    def build_chain(model_cls):
        parser = PydanticOutputParser(pydantic_object=model_cls)
        # Inject the actual format instructions into the prompt.
        prompt = PromptTemplate(
            template=BASE_PROMPT.template,
            input_variables=BASE_PROMPT.input_variables,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        llm = get_llm()
        chain = prompt | llm | parser
        return chain, parser

    @classmethod
    def run(cls, text: str):
        model_cls = cls.detect_schema(text)
        chain, parser = cls.build_chain(model_cls)
        result = chain.invoke({"input_text": text})
        # `result` is already a validated Pydantic instance.
        return result

# Helper for CLI to get a summary string.
def get_summary(obj):
    return summarize(obj)
