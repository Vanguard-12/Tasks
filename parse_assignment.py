import sys
import os
from typing import List

from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser


class AssignmentCard(BaseModel):
    """Structured representation of a single assignment description."""

    title: str = Field(..., description="Short title of the assignment")
    subject: str = Field(..., description="Subject or topic the assignment relates to")
    deadline_hint: str = Field(..., description="Free‑form hint about the deadline, e.g., 'к пятнице' or 'next Monday'")
    deliverable_type: str = Field(..., description="What should be delivered (report, code, presentation, etc.)")
    grading_hints: List[str] = Field(..., description="List of aspects mentioned for grading")


def build_chain() -> callable:
    """Construct the LangChain chain: PromptTemplate → ChatOpenAI → PydanticOutputParser.

    Returns
    -------
    callable
        A function that accepts a dict with key ``user_input`` and returns an ``AssignmentCard``.
    """
    # Structured output parser based on the Pydantic model
    parser = PydanticOutputParser(pydantic_object=AssignmentCard)

    # Prompt that asks the model to output JSON matching the parser's format instructions
    template = (
        "You are an assistant that extracts assignment details from a user‑provided description.\n"
        "Extract the fields defined in the JSON schema below and output ONLY a JSON object that conforms to it.\n"
        "{format_instructions}\n\n"
        "User description: {user_input}\n"
    )

    prompt = PromptTemplate(
        template=template,
        input_variables=["user_input"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # The LLM – configuration is taken from environment variables (e.g., OPENAI_API_KEY)
    llm = ChatOpenAI()

    # Chain: prompt -> llm -> parser
    chain = prompt | llm | parser
    return chain


def read_input() -> str:
    """Read a single assignment description either from the first CLI argument or from stdin."""
    if len(sys.argv) > 1:
        # Join all arguments after the script name to allow spaces without quoting
        return " ".join(sys.argv[1:])
    # If no argument, read the whole stdin stream
    return sys.stdin.read().strip()


def main() -> None:
    user_input = read_input()
    if not user_input:
        print("Error: No assignment description provided. Pass it as an argument or pipe it via stdin.", file=sys.stderr)
        sys.exit(1)

    chain = build_chain()
    try:
        result: AssignmentCard = chain.invoke({"user_input": user_input})
    except Exception as exc:
        print(f"Failed to parse assignment description: {exc}", file=sys.stderr)
        sys.exit(1)

    # Print the validated model as a dictionary
    print(result.model_dump())
    # Print a concise human‑readable summary
    summary = f"{result.title} – {result.deliverable_type} (deadline: {result.deadline_hint})"
    print(summary)


if __name__ == "__main__":
    # Load environment variables from a .env file if present (optional, no hard‑coded keys)
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        pass
    main()
