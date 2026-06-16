import random

def unreliable_tool(task: str) -> str:
    """A toy tool that fails with ~30% probability.

    For the demo we only understand simple arithmetic tasks like "Вычисли 2+2".
    If the task contains a '+' we evaluate it safely; otherwise we return a placeholder.
    """
    # Simulate random failure
    if random.random() < 0.3:
        raise ValueError("Tool failed")

    # Very naive arithmetic parser – only for the demo
    try:
        # Extract numbers and operator
        parts = task.replace("Вычисли", "").strip().split()
        if len(parts) == 3 and parts[1] == "+":
            a = int(parts[0])
            b = int(parts[2])
            return str(a + b)
    except Exception:
        pass
    # Fallback result
    return "result"
