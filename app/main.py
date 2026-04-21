from fastapi import FastAPI, UploadFile, File, HTTPException

from app.schemas import AskResponse
from app.stt_elevenlabs import transcribe_audio
from app.retrieval import retrieve_chunks
from app.prompt_builder import build_system_prompt, build_user_prompt
from app.llm_remote import generate_answer
from app.tts_elevenlabs import synthesize_speech
from app.rag_index import get_collection
from app.query_normalizer import normalize_query
from app.query_repair import repair_query
from app.spoken_text import beautify_query_for_display, normalize_for_tts


app = FastAPI()


def _looks_like_question(text: str) -> bool:
    if not text:
        return False

    q = text.strip().lower()

    question_starters = [
        "wer", "was", "wann", "wo", "woher", "wie", "warum", "wieso",
        "welcher", "welche", "welches", "von wem", "ist", "sind",
        "kann", "koennte", "könnte", "hat", "haben"
    ]

    return any(q.startswith(starter + " ") or q == starter for starter in question_starters)


def _is_implausible_transcript(
    raw_text: str,
    normalized_query: str,
    repaired_query: str = "",
    repair_intent: str = "unknown",
    repair_entities: list[str] | None = None,
    repair_confidence: float = 0.0,
) -> bool:
    raw = (raw_text or "").strip().lower()
    norm = (normalized_query or "").strip().lower()
    repaired = (repaired_query or "").strip().lower()
    repair_entities = repair_entities or []

    if not raw or len(raw) < 6:
        return True

    obvious_gibberish = [
        "wir haben abgetrocknet",
        "can't leave the bridge dryly",
        "cant leave the bridge dryly",
        "unlimited bridge to try me",
        "am liebste wojciech fugner",
        "dann liebte wojciech van moor",
    ]

    if raw in obvious_gibberish or norm in obvious_gibberish or repaired in obvious_gibberish:
        return True

    english_noise_markers = [
        "can't", "cant", "bridge", "dryly", "unlimited", "try me"
    ]
    if sum(1 for token in english_noise_markers if token in raw) >= 2:
        return True

    # Wenn die reparierte Anfrage klar genug ist, nicht zu früh verwerfen.
    if repair_confidence >= 0.85 and repair_intent != "unknown":
        return False

    # Bridget Riley 
    if repair_intent == "artist" and "bridget riley" in repair_entities:
        return False

    if ("bridget" in repaired or "riley" in repaired) and repair_intent == "artist" and repair_confidence >= 0.5:
        return False

    # Ebenso bei klar erkannten Künstler- oder Werkfragen toleranter sein
    if repair_intent in {"artist", "artwork", "general"} and repair_entities and repair_confidence >= 0.6:
        return False

    if not _looks_like_question(norm) and not _looks_like_question(repaired):
        return True

    return False


def _build_retry_response(transcript: str, display_text: str) -> AskResponse:
    answer_text = (
        "Ich konnte deine Frage akustisch nicht zuverlässig verstehen. "
        "Bitte stelle sie noch einmal kurz und deutlich."
    )
    audio_base64 = synthesize_speech(normalize_for_tts(answer_text))

    return AskResponse(
        transcript=transcript,
        display_text=display_text,
        answer_text=answer_text,
        audio_base64=audio_base64,
    )


@app.get("/health")
def health():
    collection = get_collection()
    count = collection.count()
    return {"status": "ok", "collection_count": count}


@app.post("/ask", response_model=AskResponse)
async def ask(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        transcript = transcribe_audio(audio_bytes, filename=audio.filename or "audio.wav")

        normalized_query = normalize_query(transcript)
        repaired = repair_query(transcript, normalized_query)

        display_text = beautify_query_for_display(
            raw_text=transcript,
            normalized_query=normalized_query,
            repaired_query=repaired.repaired_text,
        )

        print("\n=== TRANSCRIPT ===")
        print(transcript)
        print("\n=== NORMALIZED QUERY ===")
        print(normalized_query)
        print("\n=== REPAIRED QUERY ===")
        print(repaired.repaired_text)
        print("\n=== REPAIR META ===")
        print({
            "intent": repaired.intent,
            "entities": repaired.entities,
            "artist_entity": repaired.artist_entity,
            "artwork_entity": repaired.artwork_entity,
            "general_entity": repaired.general_entity,
            "forced_source_hint": repaired.forced_source_hint,
            "confidence": repaired.confidence,
        })
        print("\n=== DISPLAY TEXT ===")
        print(display_text)

        if _is_implausible_transcript(
            raw_text=transcript,
            normalized_query=normalized_query,
            repaired_query=repaired.repaired_text,
            repair_intent=repaired.intent,
            repair_entities=repaired.entities,
            repair_confidence=repaired.confidence,
        ):
            print("\n=== STT QUALITY CHECK ===")
            print("Transcript classified as implausible. Returning retry response.")

            retry_response = _build_retry_response(transcript, display_text)

            print("\n=== ANSWER ===")
            print(retry_response.answer_text)
            print("\n=== TTS TEXT ===")
            print(normalize_for_tts(retry_response.answer_text))

            return retry_response

        chunks = retrieve_chunks(
            query=repaired.repaired_text,
            intent_hint=repaired.intent,
            forced_source_hint=repaired.forced_source_hint,
            entity_hints={
                "artist": repaired.artist_entity,
                "artwork": repaired.artwork_entity,
                "general": repaired.general_entity,
            },
        )

        print("\n=== RETRIEVED CHUNKS ===")
        for i, chunk in enumerate(chunks, start=1):
            meta = chunk.get("metadata", {})
            print(f"\n--- Chunk {i} ---")
            print(f"score: {chunk.get('score')}")
            print(f"distance: {chunk.get('distance')}")
            print(f"source: {meta.get('source')}")
            print(f"category: {meta.get('category')}")
            print(f"filename: {meta.get('filename')}")
            print(f"text preview: {chunk.get('text', '')[:500]}")

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(
            query=normalized_query,
            chunks=chunks,
            repaired_query=repaired.repaired_text,
            intent=repaired.intent,
        )

        print("\n=== USER PROMPT ===")
        print(user_prompt)

        answer_text = generate_answer(system_prompt=system_prompt, user_prompt=user_prompt)

        print("\n=== ANSWER ===")
        print(answer_text)

        tts_text = normalize_for_tts(answer_text)

        print("\n=== TTS TEXT ===")
        print(tts_text)

        audio_base64 = synthesize_speech(tts_text)

        return AskResponse(
            transcript=transcript,
            display_text=display_text,
            answer_text=answer_text,
            audio_base64=audio_base64,
        )

    except Exception as e:
        print("\n=== ERROR ===")
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))