import sys
from pathlib import Path
import traceback

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import DOCS_PATH, CHROMA_PATH
from app.rag_index import get_collection
from app.query_normalizer import normalize_query
from app.query_repair import repair_query
from app.retrieval import retrieve_chunks
from app.prompt_builder import build_system_prompt, build_user_prompt


def print_header(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    try:
        print_header("SMOKE TEST START")

        print(f"Projektwurzel: {ROOT_DIR}")
        print(f"DOCS_PATH: {DOCS_PATH}")
        print(f"CHROMA_PATH: {CHROMA_PATH}")

        docs_dir = ROOT_DIR / DOCS_PATH
        if docs_dir.exists():
            print(f"[OK] Docs-Verzeichnis gefunden: {docs_dir}")
        else:
            print(f"[FEHLER] Docs-Verzeichnis nicht gefunden: {docs_dir}")
            return

        collection = get_collection()
        count = collection.count()
        print(f"[OK] Chroma Collection erreichbar. Chunk-Anzahl: {count}")

        if count == 0:
            print("[WARNUNG] Collection ist leer. Bitte zuerst den Index bauen.")
            return

        test_query = "Wann erschien das Werk B dreizehn von Wojciech Fangor?"
        print_header(f"TEST QUERY: {test_query}")

        normalized = normalize_query(test_query)
        repaired = repair_query(test_query, normalized)

        print(f"Raw:         {test_query}")
        print(f"Normalized:  {normalized}")
        print(f"Repaired:    {repaired.repaired_text}")
        print(f"Intent:      {repaired.intent}")
        print(f"Entities:    {repaired.entities}")
        print(f"Forced hint: {repaired.forced_source_hint}")
        print(f"Confidence:  {repaired.confidence:.2f}")

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

        print(f"[OK] Retrieval erfolgreich. Treffer: {len(chunks)}")

        if not chunks:
            print("[WARNUNG] Keine Chunks zurückgegeben.")
            return

        for i, chunk in enumerate(chunks[:4], start=1):
            meta = chunk.get("metadata", {})
            print(f"\nTreffer {i}")
            print(f"  Quelle:    {meta.get('source')}")
            print(f"  Kategorie: {meta.get('category')}")
            print(f"  Datei:     {meta.get('filename')}")
            print(f"  Score:     {chunk.get('score')}")
            print(f"  Distance:  {chunk.get('distance')}")
            preview = chunk.get("text", "")[:220].replace("\n", " ")
            print(f"  Text:      {preview}...")

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(
            query=normalized,
            chunks=chunks,
            repaired_query=repaired.repaired_text,
            intent=repaired.intent,
        )

        print_header("PROMPT BUILD")
        print("[OK] System Prompt erzeugt.")
        print(system_prompt[:500] + "...")

        print("\n[OK] User Prompt erzeugt.")
        print(user_prompt[:1200] + "...")

        print_header("SMOKE TEST ERFOLGREICH")

    except Exception as e:
        print_header("SMOKE TEST FEHLGESCHLAGEN")
        print(f"Fehler: {repr(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()