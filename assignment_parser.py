import os
import sys
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()


class AssignmentCard(BaseModel):
    """Flat representation of a single assignment description.

    The fields are deliberately simple so that they can be filled by a language model
    without requiring complex nested structures.
    """

    title: str = Field(
        description="A concise title for the assignment, ideally one‑sentence."
    )
    subject: str = Field(
        description="The academic subject or course the assignment belongs to."
    )
    deadline_hint: str = Field(
        description="A short, human‑readable hint about the deadline (e.g., 'by Friday', 'next Monday')."
    )
    deliverable_type: str = Field(
        description="What needs to be submitted – e.g., 'report', 'code', 'presentation', 'essay', etc."
    )
    grading_hints: List[str] = Field(
        description="A list of criteria or aspects mentioned in the description that will be used for grading."
    )


def build_chain() -> "langchain_core.runnables.base.Runnable":
    """Construct the LangChain chain: Prompt → LLM → Pydantic parser.

    Returns
    -------
    Runnable
        A chain that accepts a single string (the raw assignment description) and
        returns an ``AssignmentCard`` instance.
    """

    # Initialise the structured output parser with our Pydantic model
    parser = PydanticOutputParser(pydantic_object=AssignmentCard)

    # Prompt template – we embed the parser's format instructions so the model
    # knows exactly how to format its answer.
    template = (
        "You are an assistant that extracts structured information from a short "
        "assignment description. Extract the fields defined in the JSON schema below. "
        "Return ONLY the JSON object (no extra text).\n\n"
        "{format_instructions}\n\n"
        "Assignment description: {task_description}"
    )
    prompt = PromptTemplate(
        template=template,
        input_variables=["task_description"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Initialise the LLM – we rely on the OPENAI_API_KEY environment variable.
    # The model name can be overridden via the OPENAI_MODEL env var if desired.
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))

    # Build the chain: prompt -> llm -> parser
    chain = prompt | llm | parser
    return chain


def main(raw_description: str) -> None:
    """Run the extraction chain and print results.

    Parameters
    ----------
    raw_description: str
        The informal assignment text provided by the user.
    """
    if not raw_description:
        print("Error: No assignment description provided.")
        sys.exit(1)

    chain = build_chain()
    try:
        card: AssignmentCard = chain.invoke({"task_description": raw_description})
    except Exception as exc:
        print(f"Failed to parse assignment description: {exc}")
        sys.exit(1)

    # Print the validated model data
    print("--- Structured Assignment Card (validated) ---")
    print(card.model_dump())
    print()

    # Print a concise human‑readable summary
    summary = (
        f"{card.title} – {card.deliverable_type} – due {card.deadline_hint}. "
        f"Subject: {card.subject}. Grading hints: {', '.join(card.grading_hints)}"
    )
    print("--- Human‑readable summary ---")
    print(summary)


if __name__ == "__main__":
    # Accept the raw description either as a command‑line argument or via stdin.
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
    else:
        print("Enter the assignment description (end with Ctrl‑D):")
        input_text = sys.stdin.read().strip()
    main(input_text)
