import re
import unicodedata
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
    "aus", "bei", "über", "sich", "man", "noch", "auch", "bild", "werk", "kunstwerk",
    "bitte", "kurz", "deutlich", "sagen", "mal", "eigentlich", "denn",
}

FORCED_SOURCE_BY_ARTIST = {
    "victor vasarely": "artists/vasarely.md",
    "wojciech fangor": "artists/fangor.md",
    "bridget riley": "artists/riley.md",
    "wassily kandinsky": "artists/kandinsky.md",
    "julian stanczak": "artists/stanczak.md",
    "margaret wenstrup": "artists/wenstrup.md",
    "edna andrade": "artists/andrade.md",
}

FORCED_SOURCE_BY_ARTWORK = {
    "im schwarzen kreis": "artworks/kandinsky_im_schwarzen_kreis.md",
    "boglar i": "artworks/vasarely_boglar_I.md",
    "yabla": "artworks/vasarely_yabla.md",
    "klepsydra 1": "artworks/riley_klepsydra_1.md",
    "shih-li": "artworks/riley_shih-li.md",
    "kreisel": "artworks/wenstrup_kreisel.md",
    "zittern": "artworks/riley_zittern.md",
    "b13": "artworks/fangor_b13.md",
    "b15": "artworks/fangor_b15.md",
    "e37": "artworks/fangor_e37.md",
    "e47": "artworks/fangor_e47.md",
    "4-64": "artworks/andrade_farbbewegung.md",
    "spätes leuchten": "artworks/stanczak_spaetes_leuchten.md",
    "abstoßende anziehung": "artworks/stanczak_abstossende_anziehung.md",
    "flüchtige bewegung": "artworks/stanczak_fluechtige_bewegung.md",
}

FORCED_SOURCE_BY_GENERAL = {
    "op-art": "general/op_art_general_infos.md",
    "space age": "general/space_age_general_infos.md",
    "vierte dimension": "general/kandinsky_fourth_dimension.md",
}


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )


def normalize_for_match(text: str) -> str:
    text = (text or "").lower().strip()
    text = _strip_accents(text)
    text = text.replace("ß", "ss")
    text = text.replace("-", "_")
    text = re.sub(r"[^a-z0-9äöü_ ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    text = normalize_for_match(text)
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

    return len(overlap) / max(len(q), 1)


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


def _detect_query_intent(query: str) -> str:
    q = normalize_for_match(query)
    tokens = set(normalize_tokens(tokenize(q)))

    artist_markers = {
        "lebte", "geboren", "starb", "gestorben", "biografie", "biographie",
        "kunstler", "kuenstler", "maler", "person",
    }
    artwork_markers = {
        "gemalt", "entstand", "entstanden", "jahr", "werk", "bild", "titel",
    }
    general_markers = {
        "bedeutung", "stil", "wahrnehmung", "space", "age", "op", "art",
        "dimension", "definieren", "definition",
    }

    if tokens.intersection(artist_markers):
        return "artist"
    if tokens.intersection(artwork_markers):
        return "artwork"
    if tokens.intersection(general_markers):
        return "general"

    if any(name in q for name in ["vasarely", "fangor", "riley", "kandinsky", "stanczak", "wenstrup", "andrade"]):
        return "artist"

    return "unknown"


def get_forced_source(
    query: str,
    intent_hint: Optional[str] = None,
    forced_source_hint: Optional[str] = None,
    entity_hints: Optional[dict] = None,
) -> Optional[str]:
    if forced_source_hint:
        print(f"=== DIRECT SOURCE MATCH === {forced_source_hint} (hint)")
        return forced_source_hint

    entity_hints = entity_hints or {}
    artist = entity_hints.get("artist")
    artwork = entity_hints.get("artwork")
    general = entity_hints.get("general")

    if intent_hint == "artwork" and artwork and artwork in FORCED_SOURCE_BY_ARTWORK:
        source = FORCED_SOURCE_BY_ARTWORK[artwork]
        print(f"=== DIRECT SOURCE MATCH === {source} (artwork entity)")
        return source

    if intent_hint == "artist" and artist and artist in FORCED_SOURCE_BY_ARTIST:
        source = FORCED_SOURCE_BY_ARTIST[artist]
        print(f"=== DIRECT SOURCE MATCH === {source} (artist entity)")
        return source

    if intent_hint == "general" and general and general in FORCED_SOURCE_BY_GENERAL:
        source = FORCED_SOURCE_BY_GENERAL[general]
        print(f"=== DIRECT SOURCE MATCH === {source} (general entity)")
        return source

    q = normalize_for_match(query)
    compact = re.sub(r"[^a-z0-9äöüß]", "", q)

    forced_map = [
        (["im schwarzen kreis", "schwarzen kreis", "imschwarzenkreis", "schwarzenkreis"], "artworks/kandinsky_im_schwarzen_kreis.md"),
        (["boglar i", "boglar eins", "boglari", "boglar1"], "artworks/vasarely_boglar_I.md"),
        (["yabla"], "artworks/vasarely_yabla.md"),
        (["klepsydra", "klepsydra1"], "artworks/riley_klepsydra_1.md"),
        (["kreisel"], "artworks/wenstrup_kreisel.md"),
        (["b13"], "artworks/fangor_b13.md"),
        (["b15"], "artworks/fangor_b15.md"),
        (["e37"], "artworks/fangor_e37.md"),
        (["e47"], "artworks/fangor_e47.md"),
        (["shihli", "shih-li"], "artworks/riley_shih-li.md"),
        (["zittern"], "artworks/riley_zittern.md"),
        (["farbbewegung", "464", "4-64"], "artworks/andrade_farbbewegung.md"),
        (["abstossende anziehung", "abstossendeanziehung"], "artworks/stanczak_abstossende_anziehung.md"),
        (["fluechtige bewegung", "fluechtigebewegung"], "artworks/stanczak_fluechtige_bewegung.md"),
        (["spaetes leuchten", "spaetesleuchten"], "artworks/stanczak_spaetes_leuchten.md"),

        (["victor vasarely", "vasarely"], "artists/vasarely.md"),
        (["wojciech fangor", "fangor"], "artists/fangor.md"),
        (["bridget riley", "riley"], "artists/riley.md"),
        (["wassily kandinsky", "kandinsky"], "artists/kandinsky.md"),
        (["julian stanczak", "stanczak"], "artists/stanczak.md"),
        (["margaret wenstrup", "wenstrup"], "artists/wenstrup.md"),
        (["edna andrade", "andrade"], "artists/andrade.md"),

        (["opart", "op art", "op-art"], "general/op_art_general_infos.md"),
        (["space age", "spaceage"], "general/space_age_general_infos.md"),
        (["vierte dimension"], "general/kandinsky_fourth_dimension.md"),
    ]

    for aliases, source in forced_map:
        for alias in aliases:
            alias_norm = normalize_for_match(alias)
            alias_compact = re.sub(r"[^a-z0-9äöüß]", "", alias_norm)

            if alias_norm in q or alias_compact in compact:
                print(f"=== DIRECT SOURCE MATCH === {source}")
                return source

    print("=== DIRECT SOURCE MATCH === None")
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


def _score_chunk(
    query_tokens: list[str],
    query_intent: str,
    text: str,
    meta: dict,
    distance: float,
    forced_source: Optional[str],
    entity_hints: Optional[dict],
) -> float:
    entity_hints = entity_hints or {}

    source = meta.get("source", "")
    category = meta.get("category", "")
    filename = meta.get("filename", "")

    filename_tokens = normalize_tokens(tokenize(filename))
    source_tokens = normalize_tokens(tokenize(source))
    text_tokens = normalize_tokens(tokenize(text[:1200]))

    score = -distance

    score += overlap_score(query_tokens, filename_tokens) * 5.0
    score += overlap_score(query_tokens, source_tokens) * 3.0
    score += overlap_score(query_tokens, text_tokens) * 2.4

    if forced_source and source == forced_source:
        score += 12.0

    if query_intent == "artist":
        if category == "artists":
            score += 5.0
        elif category == "artworks":
            score -= 2.0
        elif category == "general":
            score -= 1.0

    elif query_intent == "artwork":
        if category == "artworks":
            score += 5.5
        elif category == "artists":
            score -= 1.0
        elif category == "general":
            score -= 0.5

    elif query_intent == "general":
        if category == "general":
            score += 4.5
        elif category == "artists":
            score -= 0.6
        elif category == "artworks":
            score -= 0.4

    artist = entity_hints.get("artist")
    artwork = entity_hints.get("artwork")
    general = entity_hints.get("general")

    if artist:
        artist_tokens = normalize_tokens(tokenize(artist))
        score += overlap_score(artist_tokens, text_tokens) * 3.0
        score += overlap_score(artist_tokens, filename_tokens) * 4.0

    if artwork:
        artwork_tokens = normalize_tokens(tokenize(artwork))
        score += overlap_score(artwork_tokens, text_tokens) * 3.6
        score += overlap_score(artwork_tokens, filename_tokens) * 5.0

    if general:
        general_tokens = normalize_tokens(tokenize(general))
        score += overlap_score(general_tokens, text_tokens) * 2.2
        score += overlap_score(general_tokens, filename_tokens) * 3.0

    lowered_text = normalize_for_match(text)
    lowered_filename = normalize_for_match(filename)

    if artist and normalize_for_match(artist) in lowered_text:
        score += 2.8
    if artwork and normalize_for_match(artwork) in lowered_text:
        score += 3.0
    if artist and normalize_for_match(artist) in lowered_filename:
        score += 3.5
    if artwork and normalize_for_match(artwork) in lowered_filename:
        score += 4.0

    chunk_index = meta.get("chunk_index")
    if isinstance(chunk_index, int):
        score += max(0, 1.0 - (chunk_index * 0.08))

    return score


def retrieve_chunks(
    query: str,
    top_k: int = RAG_TOP_K,
    intent_hint: Optional[str] = None,
    forced_source_hint: Optional[str] = None,
    entity_hints: Optional[dict] = None,
) -> list[dict]:
    entity_hints = entity_hints or {}

    query_tokens = normalize_tokens(tokenize(query))
    query_intent = intent_hint if intent_hint and intent_hint != "unknown" else _detect_query_intent(query)

    forced_source = get_forced_source(
        query=query,
        intent_hint=query_intent,
        forced_source_hint=forced_source_hint,
        entity_hints=entity_hints,
    )

    forced_chunks = load_direct_source_chunks(forced_source, limit=4) if forced_source else []
    forced_ids = {chunk["id"] for chunk in forced_chunks}

    collection = get_collection()
    query_embedding = embed_texts([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=20,
    )

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks = list(forced_chunks)

    for i in range(len(ids)):
        chunk_id = ids[i]
        text = docs[i] if i < len(docs) else ""
        meta = metas[i] if i < len(metas) else {}
        distance = distances[i] if i < len(distances) else 999.0

        if chunk_id in forced_ids:
            continue

        score = _score_chunk(
            query_tokens=query_tokens,
            query_intent=query_intent,
            text=text,
            meta=meta,
            distance=distance,
            forced_source=forced_source,
            entity_hints=entity_hints,
        )

        chunks.append({
            "id": chunk_id,
            "text": text,
            "metadata": meta,
            "distance": distance,
            "score": score,
        })

    chunks.sort(key=lambda x: x["score"], reverse=True)

    if not forced_source:
        diversified = []
        per_source_count = {}

        for chunk in chunks:
            source = chunk.get("metadata", {}).get("source", "unknown")
            current_count = per_source_count.get(source, 0)

            if current_count >= 2:
                continue

            diversified.append(chunk)
            per_source_count[source] = current_count + 1

            if len(diversified) >= top_k:
                break

        return diversified

    return chunks[:top_k]