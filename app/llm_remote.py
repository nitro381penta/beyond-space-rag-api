from openai import OpenAI
from app.config import OPENAI_MODEL, OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def ask_remote_llm(messages: list) -> str:
    system_text = ""
    user_text = ""

    for msg in messages:
        if msg.get("role") == "system":
            system_text = msg.get("content", "")
        elif msg.get("role") == "user":
            user_text = msg.get("content", "")

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=system_text,
        input=user_text,
    )

    text = response.output_text.strip()

    if not text:
        raise RuntimeError("Remote LLM returned empty content.")

    return text


def generate_answer(system_prompt: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return ask_remote_llm(messages)