from typing import Type

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser

from .prompts import build_prompt


def get_chain(pydantic_model: Type) -> "Runnable":
    """Build a LangChain chain: PromptTemplate -> LLM -> PydanticOutputParser.
    """
    parser = PydanticOutputParser(pydantic_object=pydantic_model)
    prompt = build_prompt(parser.get_format_instructions())
    # Initialize LLM; temperature 0 for deterministic output
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    # Chain using the pipe operator
    chain = prompt | llm | parser
    return chain
