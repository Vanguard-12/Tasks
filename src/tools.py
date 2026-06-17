import random


def unreliable_tool(task: str) -> str:
    """Simulates an unreliable tool.

    With ~30% probability it raises a ``ValueError`` to emulate a failure.
    For simple arithmetic tasks like "Вычисли 2+2" it evaluates the expression
    and returns the result as a string.
    """
    # Simulate failure
    if random.random() < 0.30:
        raise ValueError("simulated failure")

    # Very naive handling of simple arithmetic expressed in Russian "Вычисли a+b"
    # Extract numbers and compute the sum. This is only for demonstration.
    try:
        # Find all integers in the string
        numbers = [int(part) for part in task.split() if part.isdigit()]
        if len(numbers) >= 2:
            return str(numbers[0] + numbers[1])
    except Exception:
        pass
    # Fallback generic response
    return "result"
