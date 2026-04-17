import sys
from pathlib import Path
import traceback

# Projektwurzel zu sys.path hinzufügen
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import DOCS_PATH, CHROMA_PATH
from app.rag_index import get_collection
from app.retrieval import retrieve_chunks
from app.prompt_builder import build_messages


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

        test_query = "Wann lebte Victor Vasarely?"
        print_header(f"TEST QUERY: {test_query}")

        chunks = retrieve_chunks(test_query)
        print(f"[OK] Retrieval erfolgreich. Treffer: {len(chunks)}")

        if not chunks:
            print("[WARNUNG] Keine Chunks zurückgegeben.")
            return

        for i, chunk in enumerate(chunks[:3], start=1):
            meta = chunk.get("metadata", {})
            print(f"\nTreffer {i}")
            print(f"  Quelle:   {meta.get('source')}")
            print(f"  Kategorie:{meta.get('category')}")
            print(f"  Score:    {chunk.get('score')}")
            print(f"  Distance: {chunk.get('distance')}")
            preview = chunk.get("text", "")[:220].replace("\n", " ")
            print(f"  Text:     {preview}...")

        messages = build_messages(test_query, chunks)
        print_header("PROMPT BUILD")
        print(f"[OK] Prompt erfolgreich erzeugt. Nachrichtenanzahl: {len(messages)}")

        for i, msg in enumerate(messages, start=1):
            role = msg.get("role")
            content_preview = msg.get("content", "")[:300].replace("\n", " ")
            print(f"\nMessage {i} | role={role}")
            print(f"{content_preview}...")

        print_header("SMOKE TEST ERFOLGREICH")

    except Exception as e:
        print_header("SMOKE TEST FEHLGESCHLAGEN")
        print(f"Fehler: {repr(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()