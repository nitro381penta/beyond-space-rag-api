import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional


def _ascii(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text or "")
        if not unicodedata.combining(c)
    ).lower()


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


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


ARTIST_PATTERNS = {
    "wojciech fangor": [
        r"\bwojciech fangor\b",
        r"\bfangor\b",
        r"\bfango\b",
        r"\bfangohr\b",
        r"\bvangor\b",
        r"\bvan moor\b",
        r"\bfugner\b",
        r"\bfugnor\b",
        r"\bf[üu]gner\b",
        r"\bwoitschech fangor\b",
        r"\bwojciech\b",
    ],
    "wassily kandinsky": [
        r"\bwassily kandinsky\b",
        r"\bkandinsky\b",
        r"\bkandinski\b",
        r"\bkandisky\b",
        r"\bkandiski\b",
        r"\bbasilikum\b",
        r"\bwassili kandinsky\b",
        r"\bwassili\b",
    ],
    "bridget riley": [
        r"\bbridget riley\b",
        r"\bbridget\b",
        r"\bbrigitte\b",
        r"\bbritta\b",
        r"\briley\b",
        r"\breilly\b",
        r"\breil\b",
        r"\bdreiling\b",
        r"\bdryly\b",
    ],
    "victor vasarely": [
        r"\bvictor vasarely\b",
        r"\bvasarely\b",
        r"\bvasareli\b",
        r"\bvasarelli\b",
        r"\bbasarely\b",
        r"\bwasarely\b",
        r"\bvasarin\b",
        r"\bviktor vasarely\b",
        r"\bviktor\b",
    ],
    "julian stanczak": [
        r"\bjulian stanczak\b",
        r"\bstanczak\b",
        r"\bsta[nń]czak\b",
        r"\bjulian\b",
    ],
    "margaret wenstrup": [
        r"\bmargaret wenstrup\b",
        r"\bwenstrup\b",
        r"\bwenstrub\b",
        r"\bwenstr[üu]p\b",
        r"\bbenstrup\b",
        r"\bmargaret\b",
        r"\bmargret\b",
    ],
    "edna andrade": [
        r"\bedna andrade\b",
        r"\bandrade\b",
        r"\bedna\b",
    ],
}

ARTWORK_PATTERNS = {
    "im schwarzen kreis": [
        r"\bim schwarzen kreis\b",
        r"\bden schwarzen kreis\b",
        r"\bder schwarze kreis\b",
        r"\bschwarzen kreis\b",
    ],
    "boglar i": [
        r"\bboglar i\b",
        r"\bboglar 1\b",
        r"\bboglar eins\b",
        r"\bbukla\b",
        r"\bbuglar\b",
        r"\bbogler\b",
        r"\bbogla\b",
        r"\bboklar\b",
    ],
    "klepsydra 1": [
        r"\bklepsydra 1\b",
        r"\bklepsydra eins\b",
        r"\bclepsydra\b",
        r"\bklepsidra\b",
        r"\bkleepsydra\b",
    ],
    "kreisel": [
        r"\bkreisel\b",
    ],
    "yabla": [
        r"\byabla\b",
        r"\bjabla\b",
        r"\bjablo\b",
        r"\bjableh\b",
        r"\bjabloh\b",
    ],
    "shih-li": [
        r"\bshih-li\b",
        r"\bshih li\b",
        r"\bschi li\b",
        r"\bshi li\b",
        r"\bshili\b",
    ],
    "zittern": [
        r"\bzittern\b",
    ],
    "b13": [
        r"\bb13\b",
        r"\bb 13\b",
        r"\bb dreizehn\b",
        r"\bbee 13\b",
        r"\bbe 13\b",
        r"\bbi 13\b",
        r"\bbild 13\b",
        r"\bbeat 13\b",
    ],
    "b15": [
        r"\bb15\b",
        r"\bb 15\b",
        r"\bb fünfzehn\b",
        r"\bb funfzehn\b",
        r"\bbee 15\b",
        r"\bbe 15\b",
        r"\bbi 15\b",
        r"\bbild 15\b",
        r"\bbeat 15\b",
    ],
    "e37": [
        r"\be37\b",
        r"\be 37\b",
        r"\bi 37\b",
    ],
    "e47": [
        r"\be47\b",
        r"\be 47\b",
        r"\bi 47\b",
    ],
    "spätes leuchten": [
        r"\bspätes leuchten\b",
        r"\bspaetes leuchten\b",
        r"\bspates leuchten\b",
    ],
    "abstoßende anziehung": [
        r"\babstoßende anziehung\b",
        r"\babstossende anziehung\b",
    ],
    "flüchtige bewegung": [
        r"\bflüchtige bewegung\b",
        r"\bfluchtige bewegung\b",
        r"\bfluechtige bewegung\b",
    ],
    "4-64": [
        r"\b4-64\b",
        r"\b4 64\b",
        r"\b4\.64\b",
        r"\bfarbbewegung\b",
    ],
}

GENERAL_PATTERNS = {
    "op-art": [r"\bop art\b", r"\bop-art\b"],
    "space age": [r"\bspace age\b", r"\bspace-age\b"],
    "vierte dimension": [r"\bvierte dimension\b"],
}


def _replace_patterns(text: str, pattern_map: dict[str, list[str]]) -> tuple[str, list[str]]:
    repaired = text
    found = []

    for canonical, patterns in pattern_map.items():
        matched = False
        for pattern in patterns:
            if re.search(pattern, repaired):
                repaired = re.sub(pattern, canonical, repaired)
                matched = True
        if matched:
            found.append(canonical)

    return repaired, found


def _normalize_question_shape(text: str) -> str:
    q = _normalize_spaces((text or "").lower())

    q = re.sub(r"^sagen wir,?\s*wo die ([a-zäöüß\s\-]+) geboren$", r"wo wurde \1 geboren", q)
    q = re.sub(r"^wo die ([a-zäöüß\s\-]+) geboren$", r"wo wurde \1 geboren", q)
    q = re.sub(r"^wo ([a-zäöüß\s\-]+) geboren$", r"wo wurde \1 geboren", q)

    q = re.sub(r"^zu welcher zeit fand das space age statt$", "wann war das space age", q)
    q = re.sub(r"^zu welcher zeit war das space age$", "wann war das space age", q)

    q = re.sub(r"\berschien\b", "entstand", q)
    q = re.sub(r"\berschienen\b", "entstanden", q)

    q = re.sub(r"^lebte ([a-zäöüß][a-zäöüß\s\-]+)$", r"wann lebte \1", q)
    q = re.sub(r"^wurde ([a-zäöüß][a-zäöüß\s\-]+) geboren$", r"wann wurde \1 geboren", q)

    q = re.sub(r"\bwer hat das werk ([a-z0-9äöüß\-\s]+) gemalt\b", r"von wem ist das werk \1", q)
    q = re.sub(r"\bwer hat das ([a-z0-9äöüß\-\s]+) gemalt\b", r"von wem ist \1", q)
    q = re.sub(r"\bwer malte\b", "von wem ist", q)

    q = re.sub(r"\s+", " ", q).strip()
    return q


def _dedupe_adjacent_words(text: str) -> str:
    if not text:
        return text

    previous = None
    current = text

    while previous != current:
        previous = current
        current = re.sub(r"\b(\w+)( \1\b)+", r"\1", current)

    return current


def _dedupe_entities_in_text(text: str, canonical_entities: List[str]) -> str:
    repaired = text

    for entity in sorted(canonical_entities, key=len, reverse=True):
        pattern = rf"(?:{re.escape(entity)}\s+)+{re.escape(entity)}"
        repaired = re.sub(pattern, entity, repaired)

    repaired = _dedupe_adjacent_words(repaired)
    repaired = re.sub(r"\s+", " ", repaired).strip()
    return repaired


def _pick_entity(entities: List[str], candidates: dict[str, list[str]]) -> Optional[str]:
    for entity in entities:
        if entity in candidates:
            return entity
    return None


def _detect_intent(q: str, entities: List[str]) -> str:
    q_ascii = _ascii(q)

    if any(e in q for e in [
        "b13", "b15", "e37", "e47", "boglar i", "klepsydra 1",
        "im schwarzen kreis", "spätes leuchten", "abstoßende anziehung",
        "flüchtige bewegung", "4-64", "kreisel", "yabla", "shih-li", "zittern"
    ]):
        return "artwork"

    if any(word in q_ascii for word in ["gemalt", "entstand", "entstanden", "werk", "bild", "titel", "jahr"]):
        return "artwork"

    if any(word in q_ascii for word in ["geboren", "gestorben", "starb", "lebte", "wer ist", "woher kommt", "wo wurde"]):
        return "artist"

    if any(word in q_ascii for word in ["op art", "op-art", "space age", "vierte dimension", "definieren", "stilrichtung"]):
        return "general"

    if entities:
        if any(e in ARTWORK_PATTERNS for e in entities):
            return "artwork"
        if any(e in ARTIST_PATTERNS for e in entities):
            return "artist"
        if any(e in GENERAL_PATTERNS for e in entities):
            return "general"

    return "unknown"


def _forced_source_hint(
    artist_entity: Optional[str],
    artwork_entity: Optional[str],
    general_entity: Optional[str],
    intent: str,
) -> Optional[str]:
    artwork_to_source = {
        "im schwarzen kreis": "artworks/kandinsky_im_schwarzen_kreis.md",
        "boglar i": "artworks/vasarely_boglarI.md",
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

    artist_to_source = {
        "wojciech fangor": "artists/fangor.md",
        "wassily kandinsky": "artists/kandinsky.md",
        "bridget riley": "artists/riley.md",
        "victor vasarely": "artists/vasarely.md",
        "julian stanczak": "artists/stanczak.md",
        "margaret wenstrup": "artists/wenstrup.md",
        "edna andrade": "artists/andrade.md",
    }

    general_to_source = {
        "op-art": "general/op_art_general_infos.md",
        "space age": "general/space_age_general_infos.md",
        "vierte dimension": "general/kandinsky_fourth_dimension.md",
    }

    if intent == "artwork" and artwork_entity in artwork_to_source:
        return artwork_to_source[artwork_entity]

    if intent == "artist" and artist_entity in artist_to_source:
        return artist_to_source[artist_entity]

    if intent == "general":
        if general_entity in general_to_source:
            return general_to_source[general_entity]
        if artist_entity == "wassily kandinsky" and general_entity == "vierte dimension":
            return "general/kandinsky_fourth_dimension.md"

    return None


def repair_query(raw_text: str, normalized_text: str) -> QueryRepairResult:
    base = _normalize_spaces((normalized_text or raw_text or "").lower())
    repaired = _normalize_question_shape(base)

    repaired, found_artists = _replace_patterns(repaired, ARTIST_PATTERNS)
    repaired, found_artworks = _replace_patterns(repaired, ARTWORK_PATTERNS)
    repaired, found_general = _replace_patterns(repaired, GENERAL_PATTERNS)

    all_found = list(dict.fromkeys(found_artists + found_artworks + found_general))

    repaired = _normalize_question_shape(repaired)
    repaired = _dedupe_entities_in_text(repaired, all_found)

    artist_entity = _pick_entity(found_artists, ARTIST_PATTERNS)
    artwork_entity = _pick_entity(found_artworks, ARTWORK_PATTERNS)
    general_entity = _pick_entity(found_general, GENERAL_PATTERNS)

    intent = _detect_intent(repaired, all_found)
    forced_hint = _forced_source_hint(
        artist_entity=artist_entity,
        artwork_entity=artwork_entity,
        general_entity=general_entity,
        intent=intent,
    )

    confidence = 0.0
    if all_found:
        confidence += 0.5
    if intent != "unknown":
        confidence += 0.25
    if forced_hint:
        confidence += 0.25

    return QueryRepairResult(
        original_text=raw_text or "",
        normalized_text=normalized_text or "",
        repaired_text=repaired,
        intent=intent,
        entities=all_found,
        artist_entity=artist_entity,
        artwork_entity=artwork_entity,
        general_entity=general_entity,
        forced_source_hint=forced_hint,
        confidence=min(confidence, 1.0),
    )