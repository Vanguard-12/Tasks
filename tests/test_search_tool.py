import pytest
from search_tool import DuckDuckGoSearch


@pytest.mark.parametrize("query", ["Python programming", "LangChain tutorial"])
def test_search_returns_non_empty_string(query):
    result = DuckDuckGoSearch.search(query)
    assert isinstance(result, str)
    assert len(result) > 0
    # The result should contain at least one newline or be a single line of text.
    assert "\n" in result or len(result.split()) > 3
