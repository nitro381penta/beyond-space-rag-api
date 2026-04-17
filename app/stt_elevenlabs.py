import io
import os
import re
from difflib import get_close_matches
from typing import List, Set

import requests
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

from app.config import (
    DOCS_PATH,
    ELEVENLABS_API_KEY,
    ELEVENLABS_STT_LANGUAGE_CODE,
    ELEVENLABS_STT_MODEL_ID,
)


ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"


def list_markdown_files(root_dir: str) -> List[str]:
    paths = []
    for base, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(".md"):
                paths.append(os.path.join(base, f))
    return sorted(paths)


def extract_known_terms_from_docs(root_dir: str) -> List[str]:
    """
    Sammelt bekannte Künstler- und Werknamen aus Dateinamen.
    """
    known: Set[str] = set()

    for path in list_markdown_files(root_dir):
        filename = os.path.splitext(os.path.basename(path))[0]
        cleaned = filename.replace("_", " ").replace("-", " ").strip()
        if cleaned:
            known.add(cleaned.title())

    return sorted(known)


KNOWN_TERMS = extract_known_terms_from_docs(DOCS_PATH)


def preprocess_audio_bytes(audio_bytes: bytes) -> bytes:
    """
    Macht das Audio robuster für STT
    """
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)

    # Leichte Lautstärkeanhebung / Normalisierung
    target_dbfs = -18.0
    change_in_dbfs = target_dbfs - audio.dBFS if audio.dBFS != float("-inf") else 0
    audio = audio.apply_gain(change_in_dbfs)

    # Stille trimmen
    nonsilent = detect_nonsilent(audio, min_silence_len=200, silence_thresh=audio.dBFS - 16)
    if nonsilent:
        start = max(0, nonsilent[0][0] - 120)
        end = min(len(audio), nonsilent[-1][1] + 180)
        audio = audio[start:end]

    out = io.BytesIO()
    audio.export(out, format="wav")
    out.seek(0)
    return out.read()


def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def correct_named_entities(transcript: str, known_terms: List[str]) -> str:
    """
    Korrigiert bekannte Namen durch unscharfen Abgleich.
    """
    if not transcript or not known_terms:
        return transcript

    corrected = transcript

    # Prüfe ganze bekannte Namen zuerst
    lower_transcript = transcript.lower()

    # Wenn bereits exakter Treffer enthalten ist, nichts tun
    for term in known_terms:
        if term.lower() in lower_transcript:
            return transcript

    # Vergleiche gegen 2- bis 4-Wort-Sequenzen
    words = transcript.split()
    candidates = []

    for size in range(2, min(5, len(words) + 1)):
        for i in range(len(words) - size + 1):
            phrase = " ".join(words[i:i + size])
            candidates.append((phrase, i, i + size))

    best = None
    best_match = None

    for phrase, start, end in candidates:
        matches = get_close_matches(phrase.title(), known_terms, n=1, cutoff=0.78)
        if matches:
            best = (phrase, start, end)
            best_match = matches[0]
            break

    if best and best_match:
        _, start, end = best
        new_words = words[:start] + [best_match] + words[end:]
        corrected = " ".join(new_words)

    return corrected


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY is missing.")

    processed_audio = preprocess_audio_bytes(audio_bytes)

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    files = {
        "file": (filename, processed_audio, "audio/wav"),
    }

    data = {
        "model_id": ELEVENLABS_STT_MODEL_ID,
        "language_code": ELEVENLABS_STT_LANGUAGE_CODE,
    }

    response = requests.post(
        ELEVENLABS_STT_URL,
        headers=headers,
        files=files,
        data=data,
        timeout=90,
    )
    response.raise_for_status()

    payload = response.json()
    transcript = payload.get("text", "") or ""
    transcript = normalize_text(transcript)
    transcript = correct_named_entities(transcript, KNOWN_TERMS)

    return transcript