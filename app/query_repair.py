import re
from dataclasses import dataclass, field
from typing import List, Optional

from app.candidate_matcher import find_artist, find_artwork, find_general_topic


@dataclass
class QueryRepairResult:
    original_text: str
    normalized_text: str
    repaired_text: str
    intent: str
    entities: List[str] = field(default_factory=list)
    artist_entity: Optional[str] = None
    artwork_entity: Optional[str] = None
    general_entity: Optional[str] = None
    forced_source_hint: Optional[str] = None
    confidence: float = 0.0


ARTIST_TO_SOURCE = {
    "wojciech fangor": "artists/fangor.md",
    "wassily kandinsky": "artists/kandinsky.md",
    "bridget riley": "artists/riley.md",
    "victor vasarely": "artists/vasarely.md",
    "julian stanczak": "artists/stanczak.md",
    "margaret wenstrup": "artists/wenstrup.md",
    "edna andrade": "artists/andrade.md",
}

ARTWORK_TO_SOURCE = {
    "im schwarzen kreis": "artworks/kandinsky_im_schwarzen_kreis.md",
    "boglar i": "artworks/vasarely_boglar_I.md",
    "klepsydra 1": "artworks/riley_klepsydra_1.md",
    "kreisel": "artworks/wenstrup_kreisel.md",
    "yabla": "artworks/vasarely_yabla.md",
    "shih-li": "artworks/riley_shih-li.md",
    "zittern": "artworks/riley_zittern.md",
    "b13": "artworks/fangor_b13.md",
    "b15": "artworks/fangor_b15.md",
    "e37": "artworks/fangor_e37.md",
    "e47": "artworks/fangor_e47.md",
    "spätes leuchten": "artworks/stanczak_spaetes_leuchten.md",
    "abstoßende anziehung": "artworks/stanczak_abstossende_anziehung.md",
    "flüchtige bewegung": "artworks/stanczak_fluechtige_bewegung.md",
    "4-64": "artworks/andrade_farbbewegung.md",
}

GENERAL_TO_SOURCE = {
    "op-art": "general/op_art_general_infos.md",
    "space age": "general/space_age_general_infos.md",
    "vierte dimension": "general/kandinsky_fourth_dimension.md",
}


def _normalize_question_shape(text: str) -> str:
    q = (text or "").strip().lower()
    q = re.sub(r"\s+", " ", q)

    q = re.sub(r"^sagen wir,?\s*wo die (.+) geboren$", r"wo wurde \1 geboren", q)
    q = re.sub(r"^wo die (.+) geboren$", r"wo wurde \1 geboren", q)
    q = re.sub(r"^wo (.+) geboren$", r"wo wurde \1 geboren", q)

    q = re.sub(r"^zu welcher zeit fand das space age statt$", "wann war das space age", q)
    q = re.sub(r"^zu welcher zeit war das space age$", "wann war das space age", q)

    q = re.sub(r"\berschien\b", "entstand", q)
    q = re.sub(r"\berschienen\b", "entstanden", q)

    q = re.sub(r"^lebte (.+)$", r"wann lebte \1", q)
    q = re.sub(r"^liebte (.+)$", r"wann lebte \1", q)
    q = re.sub(r"^dann lebte (.+)$", r"wann lebte \1", q)
    q = re.sub(r"^dann lebt (.+)$", r"wann lebte \1", q)
    q = re.sub(r"^wann liebte (.+)$", r"wann lebte \1", q)

    q = re.sub(r"^wurde (.+) geboren$", r"wann wurde \1 geboren", q)

    # Harte Spezialfälle, die oft genau so aus STT kommen
    q = re.sub(r"\bunlimited bridge to try me\b", "wann lebte bridget riley", q)
    q = re.sub(r"\ban die brücke zum achen\b", "wann lebte bridget riley", q)
    q = re.sub(r"\ban die brucke zum achen\b", "wann lebte bridget riley", q)
    q = re.sub(r"\bdann lebt die bridget riley\b", "wann lebte bridget riley", q)
    q = re.sub(r"\bliebte bridget riley\b", "wann lebte bridget riley", q)
    q = re.sub(r"\bliebte britta dryly\b", "wann lebte bridget riley", q)
    q = re.sub(r"\bliebte britta dreiling\b", "wann lebte bridget riley", q)

    q = re.sub(r"\bbogolar i\b", "boglar i", q)
    q = re.sub(r"\bbogolar\b", "boglar i", q)

    q = re.sub(r"\bbazarew\b", "vasarely", q)
    q = re.sub(r"\bbazarev\b", "vasarely", q)

    q = re.sub(r"\bjoblücke\b", "yabla", q)
    q = re.sub(r"\bjoblucke\b", "yabla", q)

    q = re.sub(r"\[stimme bricht ab\]", "", q)

    q = re.sub(r"\s+", " ", q).strip()
    return q


def _detect_intent(
    q: str,
    artist_entity: Optional[str],
    artwork_entity: Optional[str],
    general_entity: Optional[str],
) -> str:
    ql = q.lower()

    if artwork_entity:
        return "artwork"

    if general_entity:
        return "general"

    if any(token in ql for token in ["geboren", "gestorben", "starb", "lebte", "wer ist", "woher kommt", "wo wurde"]):
        return "artist"

    if any(token in ql for token in ["werk", "bild", "gemalt", "entstand", "jahr", "titel"]):
        return "artwork"

    if any(token in ql for token in ["op-art", "op art", "space age", "vierte dimension", "definieren", "stilrichtung"]):
        return "general"

    if artist_entity:
        return "artist"

    return "unknown"


def _replace_artist_aliases(text: str, artist_entity: str) -> str:
    repaired = text

    if artist_entity == "wassily kandinsky":
        repaired = re.sub(r"\b(kandinsky|kandinski|kandisky|kandiski|basilikum)\b", "wassily kandinsky", repaired)

    elif artist_entity == "victor vasarely":
        repaired = re.sub(
            r"\b(vasarely|vasareli|vasarelli|bazarew|bazarev|basarely|wasarely|vasarew|vasarev)\b",
            "victor vasarely",
            repaired,
        )

    elif artist_entity == "wojciech fangor":
        repaired = re.sub(
            r"\b(fangor|fango|fangohr|van moor|vangor|fugner|fugnor)\b",
            "wojciech fangor",
            repaired,
        )

    elif artist_entity == "bridget riley":
        repaired = re.sub(
            r"\b(riley|reilly|reil|dryly|dreiling|draily|bridget|brigitte|britta|bridge)\b",
            "bridget riley",
            repaired,
        )

    elif artist_entity == "julian stanczak":
        repaired = re.sub(r"\b(stanczak|stansak|stanszak|stancak)\b", "julian stanczak", repaired)

    elif artist_entity == "margaret wenstrup":
        repaired = re.sub(r"\b(wenstrup|wenstrub|wenstrüp|benstrup)\b", "margaret wenstrup", repaired)

    elif artist_entity == "edna andrade":
        repaired = re.sub(r"\b(andrade)\b", "edna andrade", repaired)

    repaired = re.sub(rf"\b{re.escape(artist_entity)}\s+{re.escape(artist_entity)}\b", artist_entity, repaired)
    return repaired


def _replace_artwork_aliases(text: str, artwork_entity: str) -> str:
    repaired = text

    patterns = {
        "im schwarzen kreis": r"\b(im schwarzen kreis|den schwarzen kreis|der schwarze kreis|schwarzen kreis)\b",
        "boglar i": r"\b(boglar i|boglar 1|boglar eins|bogolar i|bogolar|buglar|bukla|bogler)\b",
        "klepsydra 1": r"\b(klepsydra 1|klepsydra eins|clepsydra|klepsidra)\b",
        "kreisel": r"\b(kreisel)\b",
        "yabla": r"\b(yabla|jabla|jablo|joblücke|joblucke)\b",
        "shih-li": r"\b(shih-li|shih li|schi li|shi li)\b",
        "zittern": r"\b(zittern)\b",
        "b13": r"\b(b13|b 13|b dreizehn|bee 13|be 13|bi 13)\b",
        "b15": r"\b(b15|b 15|b fünfzehn|b funfzehn)\b",
        "e37": r"\b(e37|e 37|i 37)\b",
        "e47": r"\b(e47|e 47|i 47)\b",
        "spätes leuchten": r"\b(spätes leuchten|spaetes leuchten|spates leuchten)\b",
        "abstoßende anziehung": r"\b(abstoßende anziehung|abstossende anziehung)\b",
        "flüchtige bewegung": r"\b(flüchtige bewegung|fluchtige bewegung|fluechtige bewegung)\b",
        "4-64": r"\b(4-64|4 64|4\.64|farbbewegung)\b",
    }

    pattern = patterns.get(artwork_entity)
    if pattern:
        repaired = re.sub(pattern, artwork_entity, repaired)

    repaired = re.sub(rf"\b{re.escape(artwork_entity)}\s+{re.escape(artwork_entity)}\b", artwork_entity, repaired)
    return repaired


def _build_repaired_query(
    q: str,
    artist_entity: Optional[str],
    artwork_entity: Optional[str],
    general_entity: Optional[str],
    intent: str,
) -> str:
    repaired = q

    if artist_entity:
        repaired = _replace_artist_aliases(repaired, artist_entity)

    if artwork_entity:
        repaired = _replace_artwork_aliases(repaired, artwork_entity)

    if general_entity:
        repaired = re.sub(r"\bop art\b", "op-art", repaired)
        repaired = re.sub(r"\bspace age\b", "space age", repaired)
        repaired = re.sub(r"\bvierte dimension\b", "vierte dimension", repaired)

    repaired = re.sub(r"\s+", " ", repaired).strip()

    if intent == "artist":
        if artist_entity and "lebte" in repaired:
            repaired = f"wann lebte {artist_entity}"
        elif artist_entity and "geboren" in repaired:
            repaired = f"wann wurde {artist_entity} geboren"
        elif artist_entity and repaired == artist_entity:
            repaired = f"wer ist {artist_entity}"

    elif intent == "artwork":
        if artwork_entity and "entstand" in repaired:
            if artist_entity:
                repaired = f"wann entstand das werk {artwork_entity} von {artist_entity}"
            else:
                repaired = f"wann entstand das werk {artwork_entity}"
        elif artwork_entity and "gemalt" in repaired:
            if artist_entity:
                repaired = f"wann wurde das werk {artwork_entity} von {artist_entity} gemalt"
            else:
                repaired = f"wann wurde das werk {artwork_entity} gemalt"
        elif artwork_entity and ("von wem" in repaired or "wer hat" in repaired):
            repaired = f"von wem ist das werk {artwork_entity}"
        elif artwork_entity and repaired == artwork_entity:
            repaired = f"was ist das werk {artwork_entity}"

    elif intent == "general":
        if general_entity == "op-art":
            repaired = "wie kann man op-art definieren"
        elif general_entity == "space age":
            repaired = "wann war das space age"
        elif general_entity == "vierte dimension" and artist_entity == "wassily kandinsky":
            repaired = "was bedeutete die vierte dimension für wassily kandinsky"

    repaired = re.sub(r"\s+", " ", repaired).strip()
    return repaired


def repair_query(raw_text: str, normalized_text: str) -> QueryRepairResult:
    base = _normalize_question_shape(normalized_text or raw_text or "")

    artist_match = find_artist(base)
    artwork_match = find_artwork(base)
    general_match = find_general_topic(base)

    artist_entity = artist_match.canonical if artist_match else None
    artwork_entity = artwork_match.canonical if artwork_match else None
    general_entity = general_match.canonical if general_match else None

    intent = _detect_intent(base, artist_entity, artwork_entity, general_entity)
    repaired = _build_repaired_query(base, artist_entity, artwork_entity, general_entity, intent)

    entities = [e for e in [artist_entity, artwork_entity, general_entity] if e]

    forced_source_hint = None
    if intent == "artwork" and artwork_entity in ARTWORK_TO_SOURCE:
        forced_source_hint = ARTWORK_TO_SOURCE[artwork_entity]
    elif intent == "artist" and artist_entity in ARTIST_TO_SOURCE:
        forced_source_hint = ARTIST_TO_SOURCE[artist_entity]
    elif intent == "general" and general_entity in GENERAL_TO_SOURCE:
        forced_source_hint = GENERAL_TO_SOURCE[general_entity]

    confidence = 0.0
    for match in [artist_match, artwork_match, general_match]:
        if match:
            confidence = max(confidence, match.score)

    if forced_source_hint:
        confidence = max(confidence, 0.95)
    elif entities:
        confidence = max(confidence, 0.75)

    return QueryRepairResult(
        original_text=raw_text or "",
        normalized_text=normalized_text or "",
        repaired_text=repaired,
        intent=intent,
        entities=entities,
        artist_entity=artist_entity,
        artwork_entity=artwork_entity,
        general_entity=general_entity,
        forced_source_hint=forced_source_hint,
        confidence=min(confidence, 1.0),
    )