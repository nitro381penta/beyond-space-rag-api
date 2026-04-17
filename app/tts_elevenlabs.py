import base64
import re
from typing import Dict

import requests

from app.config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_MODEL_ID,
    ELEVENLABS_VOICE_ID,
)


ELEVENLABS_TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"


GERMAN_NUMBER_WORDS: Dict[int, str] = {
    0: "null",
    1: "eins",
    2: "zwei",
    3: "drei",
    4: "vier",
    5: "fünf",
    6: "sechs",
    7: "sieben",
    8: "acht",
    9: "neun",
    10: "zehn",
    11: "elf",
    12: "zwölf",
    13: "dreizehn",
    14: "vierzehn",
    15: "fünfzehn",
    16: "sechzehn",
    17: "siebzehn",
    18: "achtzehn",
    19: "neunzehn",
    20: "zwanzig",
    30: "dreißig",
    40: "vierzig",
    50: "fünfzig",
    60: "sechzig",
    70: "siebzig",
    80: "achtzig",
    90: "neunzig",
}


MONTHS = {
    "01": "Januar",
    "02": "Februar",
    "03": "März",
    "04": "April",
    "05": "Mai",
    "06": "Juni",
    "07": "Juli",
    "08": "August",
    "09": "September",
    "10": "Oktober",
    "11": "November",
    "12": "Dezember",
}


def number_to_german(n: int) -> str:
    if n in GERMAN_NUMBER_WORDS:
        return GERMAN_NUMBER_WORDS[n]

    if n < 100:
        ones = n % 10
        tens = n - ones
        if ones == 1:
            return f"einund{GERMAN_NUMBER_WORDS[tens]}"
        return f"{GERMAN_NUMBER_WORDS[ones]}und{GERMAN_NUMBER_WORDS[tens]}"

    if n < 1000:
        hundreds = n // 100
        rest = n % 100
        prefix = "einhundert" if hundreds == 1 else f"{GERMAN_NUMBER_WORDS[hundreds]}hundert"
        return prefix if rest == 0 else f"{prefix}{number_to_german(rest)}"

    if 1000 <= n <= 2099:
        if 1000 <= n <= 1999:
            hundreds = n // 100
            rest = n % 100
            if n == 1000:
                return "eintausend"
            if hundreds == 10:
                base = "zehnhundert"
            elif hundreds == 11:
                base = "elfhundert"
            elif hundreds == 12:
                base = "zwölfhundert"
            else:
                base = f"{number_to_german(hundreds)}hundert"
            return base if rest == 0 else f"{base}{number_to_german(rest)}"

        if 2000 <= n <= 2099:
            rest = n - 2000
            return "zweitausend" if rest == 0 else f"zweitausend{number_to_german(rest)}"

    if n < 1000000:
        thousands = n // 1000
        rest = n % 1000
        prefix = "eintausend" if thousands == 1 else f"{number_to_german(thousands)}tausend"
        return prefix if rest == 0 else f"{prefix}{number_to_german(rest)}"

    return str(n)


def replace_years(text: str) -> str:
    def repl(match: re.Match) -> str:
        year = int(match.group(0))
        if 1000 <= year <= 2099:
            return number_to_german(year)
        return match.group(0)

    return re.sub(r"\b(1\d{3}|20\d{2})\b", repl, text)


def replace_date_patterns(text: str) -> str:
    # 16.04.2026 -> 16. April 2026 (danach wird 2026 noch ausgeschrieben)
    def repl_numeric_date(match: re.Match) -> str:
        day = str(int(match.group(1)))
        month = match.group(2)
        year = match.group(3)
        month_name = MONTHS.get(month, month)
        return f"{day}. {month_name} {year}"

    text = re.sub(r"\b(\d{1,2})\.(\d{2})\.(\d{4})\b", repl_numeric_date, text)

    # 1930-2008 -> 1930 bis 2008
    text = re.sub(r"\b(1\d{3}|20\d{2})\s*[-–]\s*(1\d{3}|20\d{2})\b", r"\1 bis \2", text)

    return text


def add_speaking_pauses(text: str) -> str:
    # Mehr Klarheit bei Lebensdaten und Aufzählungen
    text = re.sub(r"\bvon\s+([A-Za-zäöüÄÖÜß]+)\s+bis\s+([A-Za-zäöüÄÖÜß]+)\b", r"von \1, bis \2", text)
    text = re.sub(r":\s*", ". ", text)
    text = re.sub(r";\s*", ". ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def prepare_text_for_tts(text: str) -> str:
    text = text.strip()
    text = replace_date_patterns(text)
    text = replace_years(text)
    text = add_speaking_pauses(text)
    return text


def synthesize_speech(text: str) -> str:
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY is missing.")
    if not ELEVENLABS_VOICE_ID:
        raise ValueError("ELEVENLABS_VOICE_ID is missing.")

    spoken_text = prepare_text_for_tts(text)

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": spoken_text,
        "model_id": ELEVENLABS_MODEL_ID,
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.8,
            "style": 0.1,
            "use_speaker_boost": True,
        },
    }

    response = requests.post(ELEVENLABS_TTS_URL, json=payload, headers=headers, timeout=90)
    response.raise_for_status()

    return base64.b64encode(response.content).decode("utf-8")