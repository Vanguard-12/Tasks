from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from agent.config import Settings


class LLMError(RuntimeError):
    pass


class RuntimeLLM:
    def __init__(self, settings: Settings) -> None:
        if not settings.llm_base_url or not settings.llm_api_key:
            raise LLMError("LLM_BASE_URL and LLM_API_KEY are required.")
        self.model = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            temperature=0.1,
            max_tokens=settings.llm_max_tokens,
        )

    async def structured(self, prompt_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
        system_prompt = prompt_path.read_text(encoding="utf-8")
        payload_text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
        text = await self._invoke_text(system_prompt, payload_text)
        if not text:
            retry_prompt = (
                f"{system_prompt}\n\n"
                "The previous response was empty. Return one valid JSON object only. "
                "Do not include markdown fences or explanatory text."
            )
            text = await self._invoke_text(retry_prompt, payload_text)
        try:
            return parse_json_object(text)
        except LLMError:
            repair_prompt = (
                "Convert the following model output into one valid JSON object. "
                "Return JSON only. Do not add markdown fences, comments, or prose."
            )
            repaired = await self._invoke_text(repair_prompt, text)
            try:
                return parse_json_object(repaired)
            except LLMError:
                if prompt_path.name in {"edit_repository.md", "repair_repository.md"}:
                    return {
                        "operations": [],
                        "notes": [
                            "LLM returned invalid JSON even after repair; continuing with no edit operations."
                        ],
                    }
                raise

    async def _invoke_text(self, system_prompt: str, payload_text: str) -> str:
        response = await self.model.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=payload_text),
            ]
        )
        return str(response.content).strip()


def parse_json_object(text: str) -> dict[str, Any]:
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                value = json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                raise LLMError(f"LLM did not return valid JSON object: {text[:500]}") from exc
        else:
            raise LLMError(f"LLM did not return valid JSON object: {text[:500]}") from exc
    if not isinstance(value, dict):
        raise LLMError("LLM returned JSON, but not an object.")
    return value
