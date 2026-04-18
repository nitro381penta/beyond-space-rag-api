import re
from pathlib import Path
from typing import Optional

from app.config import RAG_TOP_K, DOCS_PATH, CHUNK_SIZE, CHUNK_OVERLAP
from app.rag_index import get_collection
from app.embeddings import embed_texts


STOPWORDS = {
    "was", "ist", "war", "bedeutete", "bedeutet", "die", "der", "das", "ein", "eine",
    "für", "von", "und", "in", "im", "am", "an", "zu", "zum", "zur", "den", "dem",
    "mit", "wie", "wurde", "gemalt", "entstanden", "entstand", "erschienen", "erschien",
    "welchem", "jahr", "wann", "welche", "welcher", "welches", "wer", "hat", "auf",
    "aus", "bei", "über", "sich", "man", "noch", "auch", "bild", "werk", "kunstwerk"
}


def tokenize(text: str) -> list[str]:
    text = text.lower().replace("-", "_")
    parts = re.split(r"[^a-zA-ZäöüÄÖÜß0-9]+|_", text)
    return [p for p in parts if p]


def normalize_tokens(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in STOPWORDS and len(t) > 0]


def overlap_score(query_tokens: list[str], candidate_tokens: list[str]) -> float:
    if not query_tokens or not candidate_tokens:
        return 0.0
    q = set(query_tokens)
    c = set(candidate_tokens)
    overlap = q.intersection(c)
    if not overlap:
        return 0.0
    return len(overlap) / max(len(c), 1)


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    return chunks


def get_forced_artwork_source(query: str) -> Optional[str]:
    q = query.lower()
    compact = re.sub(r"[^a-z0-9äöüß]", "", q)

    forced_map = [
        (["im schwarzen kreis", "schwarzen kreis", "imschwarzenkreis", "schwarzenkreis"], "artworks/kandinsky_im_schwarzen_kreis.md"),
        (["boglar i", "boglar eins", "boglari"], "artworks/vasarely_boglarI.md"),
        (["yabla"], "artworks/vasarely_yabla.md"),
        (["klepsydra", "klepsydra1"], "artworks/riley_klepsydra_1.md"),
        (["kreisel"], "artworks/wenstrup_kreisel.md"),
        (["b13"], "artworks/fangor_b13.md"),
        (["b15"], "artworks/fangor_b15.md"),
        (["e37"], "artworks/fangor_e37.md"),
        (["e47"], "artworks/fangor_e47.md"),
        (["shihli"], "artworks/riley_shih-li.md"),
        (["zittern"], "artworks/riley_zittern.md"),
        (["farbbewegung"], "artworks/andrade_farbbewegung.md"),
        (["abstossende anziehung", "abstossendeanziehung"], "artworks/stanczak_abstossende_anziehung.md"),
        (["fluechtige bewegung", "fluechtigebewegung"], "artworks/stanczak_fluechtige_bewegung.md"),
        (["spaetes leuchten", "spaetesleuchten"], "artworks/stanczak_spaetes_leuchten.md"),
    ]

    for aliases, source in forced_map:
        for alias in aliases:
            alias_compact = re.sub(r"[^a-z0-9äöüß]", "", alias.lower())
            if alias.lower() in q or alias_compact in compact:
                print(f"=== DIRECT ARTWORK MATCH === {source}")
                return source

    print("=== DIRECT ARTWORK MATCH === None")
    return None


def load_direct_source_chunks(source: str, limit: int = 4) -> list[dict]:
    file_path = Path(DOCS_PATH) / source
    if not file_path.exists():
        print("=== DIRECT SOURCE LOAD FAILED ===", str(file_path))
        return []

    text = file_path.read_text(encoding="utf-8")
    raw_chunks = split_into_chunks(text)

    result = []
    for idx, chunk_text in enumerate(raw_chunks[:limit]):
        result.append({
            "id": f"direct::{source}::{idx}",
            "text": chunk_text,
            "metadata": {
                "source": source,
                "category": source.split("/")[0] if "/" in source else "unknown",
                "filename": file_path.stem,
                "chunk_index": idx,
            },
            "distance": 0.0,
            "score": 100.0 - idx,
        })

    return result


def retrieve_chunks(query: str, top_k: int = RAG_TOP_K) -> list:
    query_tokens = normalize_tokens(tokenize(query))

    forced_source = get_forced_artwork_source(query)
    forced_chunks = load_direct_source_chunks(forced_source, limit=4) if forced_source else []
    forced_ids = {chunk["id"] for chunk in forced_chunks}

    collection = get_collection()
    query_embedding = embed_texts([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=16,
    )

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks = list(forced_chunks)

    for i in range(len(ids)):
        meta = metas[i] if i < len(metas) else {}
        text = docs[i] if i < len(docs) else ""
        distance = distances[i] if i < len(distances) else 999.0
        chunk_id = ids[i]

        if chunk_id in forced_ids:
            continue

        source = meta.get("source", "")
        category = meta.get("category", "")
        filename = meta.get("filename", "")

        filename_tokens = tokenize(filename)
        source_tokens = tokenize(source)
        text_tokens = tokenize(text[:900])

        score = -distance
        score += overlap_score(query_tokens, filename_tokens) * 3.0
        score += overlap_score(query_tokens, source_tokens) * 1.5
        score += overlap_score(query_tokens, text_tokens) * 1.2

        if forced_source and source == forced_source:
            score += 8.0

        if category == "artworks":
            score += 1.0

        chunks.append({
            "id": chunk_id,
            "text": text,
            "metadata": meta,
            "distance": distance,
            "score": score,
        })

    chunks.sort(key=lambda x: x["score"], reverse=True)
    return chunks[:top_k]