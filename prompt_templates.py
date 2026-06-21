from langchain_core.prompts import PromptTemplate

# The placeholder {format_instructions} will be replaced with the parser's instructions.
BASE_PROMPT = PromptTemplate(
    template="""
You are given a piece of text. Extract the required information and output it in JSON format following the schema below.

{format_instructions}

Text:
{input_text}
""",
    input_variables=["input_text"],
    partial_variables={"format_instructions": "{format_instructions}"},
)
