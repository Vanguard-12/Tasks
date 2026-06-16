import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()


class AssignmentCard(BaseModel):
    """Flat representation of a single assignment description.

    The fields are deliberately simple so that the LLM can reliably fill them
    without needing a multi‑turn dialogue.
    """

    title: str = Field(
        description="A concise title of the assignment, without the word 'assignment'"
    )
    subject: str = Field(
        description="The main subject or topic the assignment is about (e.g., 'LangChain')"
    )
    deadline_hint: Optional[str] = Field(
        default=None,
        description="A short hint about the deadline – e.g., 'к пятнице', 'by next Monday'"
    )
    deliverable_type: str = Field(
        description="What has to be delivered – e.g., 'отчёт', 'код', 'презентация'"
    )
    grading_hints: List[str] = Field(
        description="List of aspects mentioned in the description that will be used for grading"
    )

    def summary(self) -> str:
        """Return a short human‑readable summary of the card."""
        parts = [f"{self.title} – {self.deliverable_type}"]
        if self.deadline_hint:
            parts.append(f"срок: {self.deadline_hint}")
        if self.grading_hints:
            parts.append(f"оценка по: {', '.join(self.grading_hints)}")
        return ", ".join(parts) + "."


def build_chain() -> callable:
    """Create a LangChain chain that goes: Prompt → LLM → Pydantic parser.

    Returns a callable that accepts a dict with the key ``task_description``.
    """
    # Initialise the LLM – model name can be overridden via env var if desired.
    llm = ChatOpenAI(temperature=0)

    parser = PydanticOutputParser(pydantic_object=AssignmentCard)

    prompt_template = (
        "You are an assistant that extracts structured information from a short "
        "assignment description. Extract the fields defined in the JSON schema and "
        "output ONLY the JSON/YAML that matches the schema. Do not add any extra text.\n\n"
        "Task description: {task_description}\n\n"
        "{format_instructions}"
    )

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["task_description"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # The ``|`` operator builds a sequential chain.
    return prompt | llm | parser


def main() -> None:
    if len(sys.argv) > 1:
        raw_text = " ".join(sys.argv[1:])
    else:
        raw_text = input("Enter assignment description: ")

    chain = build_chain()
    try:
        card: AssignmentCard = chain.invoke({"task_description": raw_text})
    except Exception as exc:
        # Any validation or LLM errors are shown to the user.
        print("Error while processing the assignment description:")
        print(exc)
        sys.exit(1)

    # Structured output
    print("--- Structured data (model_dump) ---")
    print(card.model_dump())
    print()
    # Human‑readable summary
    print("--- Summary ---")
    print(card.summary())


if __name__ == "__main__":
    main()
