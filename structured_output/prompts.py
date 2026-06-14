from langchain_core.prompts import PromptTemplate


def build_prompt(format_instructions: str) -> PromptTemplate:
    """Build a PromptTemplate that includes the format instructions for the
    PydanticOutputParser.
    """
    template = (
        "You are given a raw text. Extract the required information and output it "
        "exactly in the JSON format described below.\n\n"
        "Text:\n{input_text}\n\n"
        "{format_instructions}"
    )
    return PromptTemplate(
        template=template,
        input_variables=["input_text"],
        partial_variables={"format_instructions": format_instructions},
    )
