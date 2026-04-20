from fastapi import FastAPI, UploadFile, File, HTTPException

from app.schemas import AskResponse
from app.stt_elevenlabs import transcribe_audio
from app.retrieval import retrieve_chunks
from app.prompt_builder import build_system_prompt, build_user_prompt
from app.llm_remote import generate_answer
from app.tts_elevenlabs import synthesize_speech
from app.rag_index import get_collection
from app.query_normalizer import normalize_query
from app.spoken_text import beautify_query_for_display, normalize_for_tts


app = FastAPI()


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
        display_text = beautify_query_for_display(transcript, normalized_query)

        print("\n=== TRANSCRIPT ===")
        print(transcript)
        print("\n=== NORMALIZED QUERY ===")
        print(normalized_query)
        print("\n=== DISPLAY TEXT ===")
        print(display_text)

        chunks = retrieve_chunks(normalized_query)

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
        user_prompt = build_user_prompt(normalized_query, chunks)

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