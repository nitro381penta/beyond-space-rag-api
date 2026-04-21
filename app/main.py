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
from app.text_cleaner import clean_answer_for_tts


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


def _contains_abort_marker(text: str) -> bool:
    t = (text or "").lower()
    abort_markers = [
        "[stimme bricht ab]",
        "stimme bricht ab",
        "[voice breaks]",
        "voice breaks",
    ]
    return any(marker in t for marker in abort_markers)


def _is_implausible_transcript(raw_text: str, normalized_query: str) -> bool:
    raw = (raw_text or "").strip().lower()
    norm = (normalized_query or "").strip().lower()

    if not raw or len(raw) < 6:
        return True

    if _contains_abort_marker(raw) or _contains_abort_marker(norm):
        return True

    obvious_gibberish = [
        "wir haben abgetrocknet",
        "can't leave the bridge dryly",
        "cant leave the bridge dryly",
        "unlimited bridge to try me",
        "an die brücke zum achen",
        "an die brucke zum achen",
        "wo die joblücke war",
        "wo die joblucke war",
        "dann lief die brille dry",
    ]

    if raw in obvious_gibberish or norm in obvious_gibberish:
        return True

    english_noise_markers = [
        "can't", "cant", "bridge", "dryly", "unlimited", "try me"
    ]
    if sum(1 for token in english_noise_markers if token in raw) >= 2:
        return True

    if not _looks_like_question(norm):
        recoverable_prefixes = [
            "liebte ",
            "dann lebt ",
            "dann lebt die ",
            "wann liebte ",
        ]
        if not any(norm.startswith(prefix) for prefix in recoverable_prefixes):
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


def _should_retry_after_repair(transcript: str, normalized_query: str, repair) -> bool:
    raw = (transcript or "").strip().lower()
    norm = (normalized_query or "").strip().lower()
    repaired = (repair.repaired_text or "").strip().lower()

    if _contains_abort_marker(raw) or _contains_abort_marker(norm) or _contains_abort_marker(repaired):
        return True

    known_bad_fragments = [
        "joblücke",
        "joblucke",
    ]
    if any(fragment in norm for fragment in known_bad_fragments):
        return True

    if _is_implausible_transcript(transcript, normalized_query) and repair.confidence < 0.72:
        return True

    if repair.intent == "unknown" and not repair.entities and not repair.forced_source_hint:
        if not _looks_like_question(norm) and not _looks_like_question(repaired):
            return True

    if "werk" in repaired and not repair.artwork_entity and repair.confidence < 0.85:
        if not any(token in repaired for token in ["wann", "von wem", "gemalt", "entstand"]):
            return True

    return False


def _retrieval_is_too_weak(chunks: list, repair) -> bool:
    if not chunks:
        return True

    top = chunks[0]
    top_score = top.get("score", -999)

    if not repair.entities and top_score < 12:
        return True

    repaired_text = (repair.repaired_text or "").lower()

    if "werk" in repaired_text and not repair.artwork_entity and top_score < 20:
        return True

    if repair.confidence < 0.40 and top_score < 14:
        return True

    return False


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
        repair = repair_query(transcript, normalized_query)
        display_text = beautify_query_for_display(transcript, repair.repaired_text or normalized_query)

        print("\n=== TRANSCRIPT ===")
        print(transcript)
        print("\n=== NORMALIZED QUERY ===")
        print(normalized_query)
        print("\n=== REPAIRED QUERY ===")
        print(repair.repaired_text)
        print("\n=== REPAIR META ===")
        print({
            "intent": repair.intent,
            "entities": repair.entities,
            "artist_entity": repair.artist_entity,
            "artwork_entity": repair.artwork_entity,
            "general_entity": repair.general_entity,
            "forced_source_hint": repair.forced_source_hint,
            "confidence": repair.confidence,
        })
        print("\n=== DISPLAY TEXT ===")
        print(display_text)

        if _should_retry_after_repair(transcript, normalized_query, repair):
            print("\n=== STT QUALITY CHECK ===")
            print("Transcript classified as implausible after repair. Returning retry response.")

            retry_response = _build_retry_response(transcript, display_text)

            print("\n=== ANSWER ===")
            print(retry_response.answer_text)
            print("\n=== TTS TEXT ===")
            print(normalize_for_tts(retry_response.answer_text))

            return retry_response

        chunks = retrieve_chunks(
            query=repair.repaired_text,
            intent_hint=repair.intent,
            forced_source_hint=repair.forced_source_hint,
            entity_hints={
                "artist": repair.artist_entity,
                "artwork": repair.artwork_entity,
                "general": repair.general_entity,
            },
        )

        if _retrieval_is_too_weak(chunks, repair):
            print("\n=== RETRIEVAL QUALITY CHECK ===")
            print("Retrieval too weak or underspecified. Returning retry response.")

            retry_response = _build_retry_response(transcript, display_text)

            print("\n=== ANSWER ===")
            print(retry_response.answer_text)
            print("\n=== TTS TEXT ===")
            print(normalize_for_tts(retry_response.answer_text))

            return retry_response

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
            repaired_query=repair.repaired_text,
            intent=repair.intent,
        )

        print("\n=== USER PROMPT ===")
        print(user_prompt)

        answer_text = generate_answer(system_prompt=system_prompt, user_prompt=user_prompt)
        answer_text = clean_answer_for_tts(answer_text)

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