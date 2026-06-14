import json
import re
from typing import Any


def safe_json_load(text: str) -> Any:
    """Extract the first JSON object from *text* and parse it.

    LLMs sometimes add explanations before/after the JSON. This helper finds the
    first balanced curly‑brace block and feeds it to ``json.loads``.
    """
    # Find the first '{' and the matching '}' using a simple stack approach
    start = text.find('{')
    if start == -1:
        raise ValueError("No JSON object found in text.")
    stack = []
    for i, ch in enumerate(text[start:]):
        if ch == '{':
            stack.append('{')
        elif ch == '}':
            stack.pop()
            if not stack:
                end = start + i + 1
                json_str = text[start:end]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to decode JSON: {e}")
    raise ValueError("Unbalanced JSON braces in text.")
