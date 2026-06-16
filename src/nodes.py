import os
import json
import logging
from typing import Any, Dict

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

# Configure a simple logger for debugging output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_llm():
    """Return a Chat model instance.

    Preference order:
    1. OpenAI if ``OPENAI_API_KEY`` is present.
    2. Ollama if ``OLLAMA_HOST`` is defined.
    Raises ``RuntimeError`` if neither is configured.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        logger.info("Using OpenAI Chat model")
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    ollama_host = os.getenv("OLLAMA_HOST")
    if ollama_host:
        logger.info("Using Ollama Chat model at %s", ollama_host)
        return ChatOllama(base_url=ollama_host, model="llama3.1:8b", temperature=0.7)
    raise RuntimeError("No LLM configuration found. Set OPENAI_API_KEY or OLLAMA_HOST.")


# Shared LLM instance – created lazily on first call
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = _get_llm()
    return _llm


# ---------------------------------------------------------------------------
# Node implementations – each receives the current state dict and returns a
# (possibly) updated dict. They are defined as ``async`` because LangGraph
# expects async callables.
# ---------------------------------------------------------------------------

async def draft_answer(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the first draft answer.

    The prompt asks for a concise (5‑10 sentence) answer to the supplied
    ``question``.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert educator. Answer the question concisely in 5‑10 sentences, using clear language.") ,
            ("human", "{question}")
        ]
    )
    chain = prompt | get_llm()
    response = await chain.ainvoke({"question": state["question"]})
    draft = response.content.strip()
    logger.info("Draft generated (round %s): %s", state.get("round", 0), draft)
    # Initialise other fields
    state.update({
        "draft": draft,
        "critique": "",
        "verdict": "",
        "round": 0,
    })
    return state


async def reflect(state: Dict[str, Any]) -> Dict[str, Any]:
    """Critique the current draft.

    The LLM is asked to return a JSON object with two keys:
    * ``verdict`` – ``"ok"`` if the draft looks good, otherwise ``"needs_revision"``.
    * ``critique`` – a short bullet‑point list (2‑3 items).
    """
    critique_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a reviewer. Evaluate the draft answer for completeness, concreteness, and lack of fluff. Return a JSON object with keys 'verdict' (either 'ok' or 'needs_revision') and 'critique' (a short bullet‑point list)."),
            ("human", "Draft:\n{draft}\n\nQuestion:\n{question}\n\nProvide your evaluation.")
        ]
    )
    chain = critique_prompt | get_llm()
    response = await chain.ainvoke({"draft": state["draft"], "question": state["question"]})
    raw = response.content.strip()
    logger.info("Raw critique output: %s", raw)
    # Try to parse JSON – the model may add extra text, so we locate the first '{'
    try:
        json_start = raw.find('{')
        parsed: Dict[str, Any] = json.loads(raw[json_start:])
    except Exception as e:
        logger.error("Failed to parse critique JSON: %s", e)
        # Fallback – treat as needs_revision with generic critique
        parsed = {"verdict": "needs_revision", "critique": "Could not parse critique; please revise."}
    state["verdict"] = parsed.get("verdict", "needs_revision")
    state["critique"] = parsed.get("critique", "")
    logger.info("Verdict: %s", state["verdict"])
    return state


async def rewrite(state: Dict[str, Any]) -> Dict[str, Any]:
    """Rewrite the draft using the critique.

    The prompt supplies the original draft, the critique, and asks the LLM to
    produce an improved version (again 5‑10 sentences). The round counter is
    incremented.
    """
    rewrite_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a writer. Improve the draft based on the given critique. Keep the answer concise (5‑10 sentences)."),
            ("human", "Draft:\n{draft}\n\nCritique:\n{critique}\n\nRewrite the draft:")
        ]
    )
    chain = rewrite_prompt | get_llm()
    response = await chain.ainvoke({"draft": state["draft"], "critique": state["critique"]})
    new_draft = response.content.strip()
    logger.info("Rewritten draft (round %s): %s", state["round"] + 1, new_draft)
    state["draft"] = new_draft
    state["round"] = state.get("round", 0) + 1
    # Reset verdict/critique for the next reflection step
    state["verdict"] = ""
    state["critique"] = ""
    return state
