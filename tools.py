# Placeholder for tool definitions used by the LangGraph agent.
# In a full implementation, define functions that conform to the LangGraph tool interface.

def get_price(city: str, date: str):
    """Mock implementation of a price retrieval tool.

    Args:
        city: Name of the city.
        date: Date string (e.g., 'today' or 'tomorrow').

    Returns:
        A string describing a fake price.
    """
    return f"Price for {city} on {date}: 1000 RUB"
