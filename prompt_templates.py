from __future__ import annotations

from langchain_core.prompts import PromptTemplate

# The templates embed the format instructions that the PydanticOutputParser provides.
# They receive two variables:
#   - format_instructions: the JSON schema instructions from the parser
#   - text: the raw input supplied by the user

PERSON_TEMPLATE = PromptTemplate(
    template="""
You are given a short free‑form description of a person. Extract the required information and output it **exactly** in the JSON format described by the format instructions.

{format_instructions}

Text:
{text}
""",
    input_variables=["format_instructions", "text"],
)

MEETING_TEMPLATE = PromptTemplate(
    template="""
You are given a short free‑form description of a meeting. Extract the required information and output it **exactly** in the JSON format described by the format instructions.

{format_instructions}

Text:
{text}
""",
    input_variables=["format_instructions", "text"],
)
