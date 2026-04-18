import re
from pathlib import Path
from typing import Optional

from app.config import RAG_TOP_K, DOCS_PATH, CHUNK_SIZE, CHUNK_OVERLAP
from app.rag_index import get_collection, list_markdown_files
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


def build_knowledge_catalog():
    files = list_markdown_files(DOCS_PATH)
    catalog = {"artists": [], "artworks": [], "general": [], "tour": []}

    for file_path in files:
        rel_path = file_path.replace("\\", "/").split("/data/docs/")[-1]
        category = rel_path.split("/")[0]
        filename = rel_path.split("/")[-1].replace(".md", "")

        item = {
            "source": rel_path,
            "filename": filename,
            "tokens": tokenize(filename),
            "category": category,
        }

        if category in catalog:
            catalog[category].append(item)

    return catalog


def detect_best_match(query: str, catalog_items: list[dict]):
    query_tokens = normalize_tokens(tokenize(query))
    best_item = None
    best_score = 0.0

    for item in catalog_items:
        score = overlap_score(query_tokens, item["tokens"])
        if score > best_score:
            best_score = score
            best_item = item

    if best_item and best_score >= 0.3:
        return {**best_item, "match_score": best_score}
    return None


def extract_special_artwork_code(query: str) -> Optional[str]:
    q = query.lower()

    patterns = [
        r"\bb\s*\.?\s*13\b",
        r"\bb\s*\.?\s*15\b",
        r"\be\s*\.?\s*37\b",
        r"\be\s*\.?\s*47\b",
    ]

    for pattern in patterns:
        m = re.search(pattern, q)
        if m:
            raw = m.group(0)
            cleaned = re.sub(r"[^a-zA-Z0-9]", "", raw).lower()
            return cleaned

    return None


def find_direct_artwork_match(query: str, catalog_artworks: list[dict]) -> Optional[dict]:
    q = query.lower()
    compact_query = re.sub(r"[^a-z0-9äöüß]", "", q)

    # Harte Direktregel für Im schwarzen Kreis
    if (
        "im schwarzen kreis" in q
        or "schwarzen kreis" in q
        or "imschwarzenkreis" in compact_query
        or "schwarzenkreis" in compact_query
    ):
        return {
            "source": "artworks/kandinsky_im_schwarzen_kreis.md",
            "filename": "kandinsky_im_schwarzen_kreis",
            "tokens": tokenize("kandinsky_im_schwarzen_kreis"),
            "category": "artworks",
            "match_score": 1.0,
        }

    # Harte Direktregel für Boglar I
    if (
        "boglar i" in q
        or "boglar eins" in q
        or "boklar eins" in q
        or "boglari" in compact_query
        or "boklareins" in compact_query
    ):
        return {
            "source": "artworks/vasarely_boglarI.md",
            "filename": "vasarely_boglarI",
            "tokens": tokenize("vasarely_boglarI"),
            "category": "artworks",
            "match_score": 1.0,
        }

    # Harte Direktregel für Yabla
    if "yabla" in q or "jabla" in q or "jableh" in q:
        return {
            "source": "artworks/vasarely_yabla.md",
            "filename": "vasarely_yabla",
            "tokens": tokenize("vasarely_yabla"),
            "category": "artworks",
            "match_score": 1.0,
        }

    special_code = extract_special_artwork_code(q)
    if special_code:
        for item in catalog_artworks:
            filename = item["filename"].lower()
            if special_code in filename:
                return item

    direct_aliases = [
        ("kreisel", ["kreisel"]),
        ("klepsydra", ["klepsydra", "klepsydra 1", "klepsydra eins", "klepsydra one"]),
        ("shihli", ["shih li", "shih-li", "shihli"]),
        ("zittern", ["zittern"]),
        ("farbbewegung", ["farbbewegung 4 64", "farbbewegung 4-64", "farbbewegung 4.64", "4 64", "4-64", "4.64"]),
        ("spaetesleuchten", ["spätes leuchten", "spaetes leuchten", "warmes leuchten"]),
        ("abstossendeanziehung", ["abstoßende anziehung", "abstossende anziehung"]),
        ("fluechtigebewegung", ["flüchtige bewegung", "fluechtige bewegung"]),
    ]

    for key, aliases in direct_aliases:
        alias_hit = False
        for alias in aliases:
            alias_compact = re.sub(r"[^a-z0-9äöüß]", "", alias.lower())
            if alias.lower() in q or alias_compact in compact_query:
                alias_hit = True
                break

        if not alias_hit:
            continue

        for item in catalog_artworks:
            filename_compact = re.sub(r"[^a-z0-9äöüß]", "", item["filename"].lower())

            if key == "kreisel" and "kreisel" in filename_compact:
                return item
            if key == "klepsydra" and "klepsydra" in filename_compact:
                return item
            if key == "shihli" and "shihli" in filename_compact:
                return item
            if key == "zittern" and "zittern" in filename_compact:
                return item
            if key == "farbbewegung" and "farbbewegung" in filename_compact:
                return item
            if key == "spaetesleuchten" and "spaetes" in filename_compact and "leuchten" in filename_compact:
                return item
            if key == "abstossendeanziehung" and "abstossende" in filename_compact and "anziehung" in filename_compact:
                return item
            if key == "fluechtigebewegung" and ("fluechtige" in filename_compact or "fluchtige" in filename_compact):
                return item

    return None


def parse_query_intent(query: str) -> dict:
    query_tokens = normalize_tokens(tokenize(query))
    catalog = build_knowledge_catalog()

    best_artist = detect_best_match(query, catalog["artists"])
    best_artwork = detect_best_match(query, catalog["artworks"])
    best_general = detect_best_match(query, catalog["general"])

    direct_artwork_match = find_direct_artwork_match(query, catalog["artworks"])
    if direct_artwork_match:
        best_artwork = {**direct_artwork_match, "match_score": 1.0}

    intent = {
        "query_tokens": query_tokens,
        "best_artist": best_artist,
        "best_artwork": best_artwork,
        "best_general": best_general,
        "prefers_artworks": False,
        "prefers_artists": False,
        "prefers_general": False,
    }

    if any(w in query_tokens for w in [
        "jahr", "wann", "gemalt", "entstanden", "entstand",
        "erschienen", "erschien", "werk", "bild", "titel"
    ]):
        intent["prefers_artworks"] = True

    if any(w in query_tokens for w in [
        "künstler", "maler", "biografie", "lebte", "lebt",
        "geboren", "starb", "gestorben"
    ]):
        intent["prefers_artists"] = True

    if any(w in query_tokens for w in [
        "op", "art", "space", "age", "wahrnehmung",
        "abstraktion", "stil", "bedeutung", "dimension"
    ]):
        intent["prefers_general"] = True

    if best_artwork:
        intent["prefers_artworks"] = True
    elif best_artist:
        intent["prefers_artists"] = True
    elif best_general:
        intent["prefers_general"] = True

    return intent


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


def load_direct_source_chunks(source: str, limit: int = 4) -> list[dict]:
    file_path = Path(DOCS_PATH) / source
    if not file_path.exists():
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
    parsed = parse_query_intent(query)
    query_tokens = parsed["query_tokens"]

    forced_chunks = []
    forced_ids = set()

    if parsed["best_artwork"]:
        forced_source = parsed["best_artwork"]["source"]
        forced_chunks = load_direct_source_chunks(forced_source, limit=4)
        forced_ids = {chunk["id"] for chunk in forced_chunks}
        print(f"=== DIRECT ARTWORK MATCH === {forced_source}")
    else:
        print("=== DIRECT ARTWORK MATCH === None")

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

        if parsed["best_artwork"] and source == parsed["best_artwork"]["source"]:
            score += 8.0
        if parsed["best_artist"] and source == parsed["best_artist"]["source"]:
            score += 3.0
        if parsed["best_general"] and source == parsed["best_general"]["source"]:
            score += 2.0

        if parsed["prefers_artworks"] and category == "artworks":
            score += 3.0
        if parsed["prefers_artworks"] and category == "artists":
            score -= 1.5

        if parsed["prefers_artists"] and category == "artists":
            score += 2.0

        if parsed["prefers_general"] and category == "general":
            score += 1.5

        if category == "tour":
            score -= 0.3

        chunks.append({
            "id": chunk_id,
            "text": text,
            "metadata": meta,
            "distance": distance,
            "score": score,
        })

    chunks.sort(key=lambda x: x["score"], reverse=True)
    return chunks[:top_k]