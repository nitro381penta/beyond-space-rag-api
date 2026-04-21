import re


def clean_answer_for_tts(text: str) -> str:
    if not text:
        return text

    cleaned = text
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("*", "")
    cleaned = cleaned.replace("#", "")
    cleaned = cleaned.replace("„", '"').replace("“", '"')
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned