from typing import Dict
from langchain_openai import OpenAI
from src.state import ReflectState

llm = OpenAI(temperature=0)


def draft_answer(state: ReflectState) -> Dict[str, str]:
    prompt = f"Write a concise answer (5–10 sentences) to the following question: {state['question']}"
    answer = llm.invoke(prompt)
    return {"draft": answer}


def reflect(state: ReflectState) -> Dict[str, str]:
    prompt = (
        f"You are a critic. Evaluate the following draft answer for completeness, specificity, and lack of filler.\n\nDraft: {state['draft']}\n\nProvide a verdict ('ok' or 'needs_revision') and 2–3 critique points separated by newlines."
    )
    response = llm.invoke(prompt)
    lines = response.splitlines()
    verdict_line = next((l for l in lines if l.lower().startswith("verdict:")), "")
    critique_lines = [l for l in lines if l.lower().startswith("critique:") or l.strip()]
    verdict = verdict_line.split(":", 1)[1].strip() if verdict_line else "needs_revision"
    critique = "\n".join(l.strip() for l in critique_lines if l.strip())
    return {"verdict": verdict, "critique": critique}


def rewrite(state: ReflectState) -> Dict[str, str]:
    prompt = (
        f"Rewrite the following draft answer to address the critique points.\n\nDraft: {state['draft']}\nCritique: {state['critique']}\n\nProvide the improved answer."
    )
    new_draft = llm.invoke(prompt)
    return {"draft": new_draft, "round": state["round"] + 1}
