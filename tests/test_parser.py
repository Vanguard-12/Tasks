import os
from unittest.mock import MagicMock, patch

import pytest

from parser import split_log, parse_log

# ---------------------------------------------------------------------------
# split_log tests – pure string manipulation, no LLM required
# ---------------------------------------------------------------------------

def test_split_log_basic():
    raw = """
200 GET /api/users duration=123ms
---
404 GET /api/orders error=\"Order not found\"
---
500 POST /api/payments error=\"Internal server error\"
"""
    blocks = split_log(raw)
    assert len(blocks) == 3
    assert "200 GET" in blocks[0]
    assert "404 GET" in blocks[1]
    assert "500 POST" in blocks[2]


def test_split_log_ignores_empty_lines():
    raw = """
200 GET /api/users duration=123ms
\n\n---\n\n404 GET /api/orders error=\"Order not found\"\n"""
    blocks = split_log(raw)
    assert len(blocks) == 2

# ---------------------------------------------------------------------------
# parse_log tests – we mock the LLM to avoid real API calls.
# ---------------------------------------------------------------------------

MOCK_OK = {
    "kind": "ok",
    "status": 200,
    "path": "/api/users",
    "duration_ms": 123,
}

MOCK_ERROR = {
    "kind": "error",
    "status": 404,
    "path": "/api/orders",
    "error_message": "Order not found",
}


@patch("parser.ChatOpenAI")
def test_parse_log_with_mocked_llm(mock_chat):
    # Configure the mock LLM to return our predefined dictionaries.
    mock_instance = MagicMock()
    # ``with_structured_output`` returns a callable that we also mock.
    def fake_with_structured_output(_):
        return lambda _: MagicMock(**{"model_dump.return_value": _})

    mock_instance.with_structured_output.side_effect = fake_with_structured_output
    mock_chat.return_value = mock_instance

    raw = """
200 GET /api/users duration=123ms
---
404 GET /api/orders error=\"Order not found\"
"""
    events = parse_log(raw)
    # Two events should be parsed.
    assert len(events) == 2
    # The mock returns objects that expose ``model_dump``; we check the underlying dict.
    assert events[0].model_dump() == MOCK_OK
    assert events[1].model_dump() == MOCK_ERROR
