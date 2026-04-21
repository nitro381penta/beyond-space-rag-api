import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.query_normalizer import normalize_query
from app.query_repair import repair_query
from app.retrieval import retrieve_chunks


TEST_CASES = [
    {
        "raw": "wann gibt der basilikum den saft",
        "expected_source": "artists/kandinsky.md",
        "description": "basilikum -> kandinsky",
    },
    {
        "raw": "wer hat das wenstrup kreisel gemalt",
        "expected_source": "artworks/wenstrup_kreisel.md",
        "description": "wenstrup kreisel -> artwork",
    },
    {
        "raw": "sagen wir, wo die bridget riley geboren",
        "expected_source": "artists/riley.md",
        "description": "kaputte Frageform -> artist birth question",
    },
    {
        "raw": "zu welcher zeit fand das space age statt",
        "expected_source": "general/space_age_general_infos.md",
        "description": "space age -> general",
    },
    {
        "raw": "was bedeutete die vierte dimension für kandinsky",
        "expected_source": "general/kandinsky_fourth_dimension.md",
        "description": "fourth dimension -> dedicated general file",
    },
    {
        "raw": "wann erschien das werk b dreizehn von wojciech fangor",
        "expected_source": "artworks/fangor_b13.md",
        "description": "b dreizehn -> b13 artwork",
    },
    {
        "raw": "wann erschien das werk e47 von wojciech fangor",
        "expected_source": "artworks/fangor_e47.md",
        "description": "e47 -> artwork",
    },
    {
        "raw": "wann erschien das werk spätes leuchten von julian stanczak",
        "expected_source": "artworks/stanczak_spaetes_leuchten.md",
        "description": "spätes leuchten -> artwork",
    },
    {
        "raw": "wie kann man op-art definieren",
        "expected_source": "general/op_art_general_infos.md",
        "description": "op-art -> general",
    },
]


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_chunk(chunk: dict, rank: int) -> None:
    meta = chunk.get("metadata", {})
    print(f"\nTreffer {rank}")
    print(f"  Quelle:    {meta.get('source')}")
    print(f"  Kategorie: {meta.get('category')}")
    print(f"  Datei:     {meta.get('filename')}")
    print(f"  Score:     {chunk.get('score')}")
    print(f"  Distance:  {chunk.get('distance')}")
    preview = chunk.get("text", "")[:220].replace("\n", " ")
    print(f"  Preview:   {preview}...")


def evaluate_case(case: dict) -> bool:
    raw = case["raw"]
    expected_source = case["expected_source"]
    description = case.get("description", "")

    print_header(f"TEST: {raw}")
    if description:
        print(f"Beschreibung: {description}")

    normalized = normalize_query(raw)
    repair = repair_query(raw, normalized)

    print("\n--- QUERY PIPELINE ---")
    print(f"Raw:               {raw}")
    print(f"Normalized:        {normalized}")
    print(f"Repaired:          {repair.repaired_text}")
    print(f"Intent:            {repair.intent}")
    print(f"Entities:          {repair.entities}")
    print(f"Forced source hint:{repair.forced_source_hint}")
    print(f"Confidence:        {repair.confidence:.2f}")

    entity_hints = {
        "artist": repair.artist_entity,
        "artwork": repair.artwork_entity,
        "general": repair.general_entity,
    }

    chunks = retrieve_chunks(
        query=repair.repaired_text,
        top_k=4,
        intent_hint=repair.intent,
        forced_source_hint=repair.forced_source_hint,
        entity_hints=entity_hints,
    )

    print("\n--- RETRIEVAL ---")
    if not chunks:
        print("Keine Treffer.")
        print(f"\n[FAIL] Erwartet: {expected_source}")
        return False

    for i, chunk in enumerate(chunks, start=1):
        print_chunk(chunk, i)

    top_source = chunks[0].get("metadata", {}).get("source")
    top_2_sources = [c.get("metadata", {}).get("source") for c in chunks[:2]]

    passed = top_source == expected_source or expected_source in top_2_sources

    print("\n--- RESULT ---")
    print(f"Erwartete Quelle: {expected_source}")
    print(f"Top-1 Quelle:     {top_source}")
    print(f"Top-2 Quellen:    {top_2_sources}")

    if passed:
        print("[PASS]")
    else:
        print("[FAIL]")

    return passed


def main() -> None:
    print_header("DEBUG EVAL START")

    total = len(TEST_CASES)
    passed = 0

    for case in TEST_CASES:
        if evaluate_case(case):
            passed += 1

    print_header("DEBUG EVAL SUMMARY")
    print(f"Bestanden: {passed}/{total}")
    print(f"Quote:     {(passed / total * 100):.1f}%")

    if passed != total:
        print("\nMindestens ein Test schlägt noch fehl. Diese Fälle solltest du als Nächstes gezielt nachschärfen.")
    else:
        print("\nAlle Tests bestanden.")


if __name__ == "__main__":
    main()