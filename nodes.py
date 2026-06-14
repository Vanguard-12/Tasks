import json
import os
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# Initialise the LLM once – you can switch model name if you use Ollama.
LLM = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

async def draft_answer(state: Dict) -> Dict:
    """Generate an initial draft answer (5‑10 sentences)."""
    prompt = (
        f"Answer the following question in 5‑10 concise sentences, focusing on clarity and completeness.\n\n"
        f"Question: {state['question']}"
    )
    response = await LLM.ainvoke([HumanMessage(content=prompt)])
    draft = response.content.strip()
    return {"draft": draft, "round": 0}

async def reflect(state: Dict) -> Dict:
    """Critique the draft and return a verdict and short critique.

    The LLM is asked to respond with a JSON object:
    {"verdict": "ok"|"needs_revision", "critique": "..."}
    """
    prompt = (
        "You are a reviewer. Evaluate the draft answer for completeness, specificity, and lack of filler. "
        "Provide a verdict: \"ok\" if the answer is satisfactory, otherwise \"needs_revision\". "
        "Also give 2‑3 concrete critique points. Respond ONLY with a JSON object in the following format: "
        "{\"verdict\": \"ok|needs_revision\", \"critique\": \"your critique here\"}.\n\n"
        f"Draft answer:\n{state['draft']}"
    )
    response = await LLM.ainvoke([HumanMessage(content=prompt)])
    try:
        data = json.loads(response.content)
        verdict = data.get("verdict", "needs_revision")
        critique = data.get("critique", "")
    except Exception:
        # Fallback parsing if LLM does not return valid JSON
        text = response.content.strip().lower()
        verdict = "ok" if "ok" in text else "needs_revision"
        critique = response.content.strip()
    return {"verdict": verdict, "critique": critique}

async def rewrite(state: Dict) -> Dict:
    """Rewrite the draft based on the critique and increment the round counter."""
    prompt = (
        "You are asked to improve the previous draft answer using the provided critique. "
        "Produce a revised answer that addresses the critique points while keeping the length 5‑10 sentences.\n\n"
        f"Original draft:\n{state['draft']}\n\nCritique:\n{state['critique']}"
    )
    response = await LLM.ainvoke([HumanMessage(content=prompt)])
    new_draft = response.content.strip()
    return {"draft": new_draft, "round": state["round"] + 1}
