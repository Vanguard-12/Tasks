import json
from typing import List, Dict

from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

# ---------------------------------------------------------------------------
# LLM configuration – подключаемся к локальному LM Studio (OpenAI‑совместимый)
# ---------------------------------------------------------------------------
llm = ChatOpenAI(
    model="<название модели в LM Studio>",  # замените на имя модели, которую вы запустили
    base_url="http://localhost:1234/v1",
    api_key=SecretStr("fake"),
    temperature=0.7,
)

# ---------------------------------------------------------------------------
# Инструмент‑субагент: генерирует примерную цену продукта в указанном городе
# ---------------------------------------------------------------------------
@tool
def get_price(product: str, city: str) -> str:
    """Генерирует markdown‑таблицу с примерной ценой продукта в городе.

    Возвращаемый формат:
    | Продукт | Цена (руб.) | Магазин |
    """
    # Создаём отдельный суб‑агент без инструментов – он лишь генерирует текст.
    sub_agent = create_agent(
        model=llm,
        tools=[],
        system_prompt=(
            "Ты генерируешь примерную цену продукта в указанном городе. "
            "Ответ дай в виде markdown‑таблицы: | Продукт | Цена (руб.) | Магазин |. "
            "Не используй никаких инструментов, просто придумай реалистичную цену и название магазина."
        ),
    )

    # Формируем запрос к суб‑агенту.
    prompt = (
        f"Сгенерируй цену для продукта **{product}** в городе **{city}** в виде markdown‑таблицы. "
        "Таблица должна содержать одну строку с продуктом, ценой (в рублях) и названием магазина."
    )

    response = sub_agent.invoke({"messages": [{"role": "human", "content": prompt}]})
    # Ответ – словарь, где последний элемент messages содержит контент.
    content = response.get("messages", [])[-1].get("content", "")
    # На случай, если модель вернёт JSON вместо markdown, пытаемся извлечь строку.
    if isinstance(content, dict) and "text" in content:
        content = content["text"]
    return content.strip()

# ---------------------------------------------------------------------------
# Главный агент – помощник по планированию покупок
# ---------------------------------------------------------------------------
main_agent = create_agent(
    model=llm,
    tools=[get_price],
    system_prompt="Ты помощник по планированию покупок",
)

def format_message(message: Dict) -> str:
    """Приводит сообщение к читаемому виду.

    Если сообщение содержит вызов инструмента – выводим его как
    get_price({'product': ..., 'city': ...}). Иначе – просто текст.
    """
    if "content" in message and message["content"]:
        return message["content"]
    # tool_calls – список, но в текущей версии LangChain обычно один.
    if "tool_calls" in message and message["tool_calls"]:
        call = message["tool_calls"][0]
        name = call.get("name")
        args = json.dumps(call.get("args", {}), ensure_ascii=False)
        return f"{name}({args})"
    return str(message)

def main() -> None:
    user_query = (
        "Помоги составить список покупок: молоко, хлеб, яблоки. "
        "Я нахожусь в Казани."
    )
    answer = main_agent.invoke({"messages": [{"role": "human", "content": user_query}]})
    messages: List[Dict] = answer.get("messages", [])
    for msg in messages:
        print("---")
        print(format_message(msg))
    print("---")
    # Финальный ответ – последний элемент messages
    if messages:
        final = messages[-1].get("content", "")
        print("\nФинальный ответ агента:\n")
        print(final)

if __name__ == "__main__":
    main()
