import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class MatchResult:
    canonical: str
    alias: str
    score: float


def _ascii(text: str) -> str:
    text = (text or "").strip().lower()
    text = "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )
    text = text.replace("ß", "ss")
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _token_overlap_score(query: str, alias: str) -> float:
    q_tokens = set(_ascii(query).split())
    a_tokens = set(_ascii(alias).split())

    if not q_tokens or not a_tokens:
        return 0.0

    overlap = q_tokens.intersection(a_tokens)
    if not overlap:
        return 0.0

    return len(overlap) / len(a_tokens)


def _substring_score(query: str, alias: str) -> float:
    q = _ascii(query)
    a = _ascii(alias)

    if not q or not a:
        return 0.0

    if a in q:
        return 1.0

    return 0.0


def _best_match(query: str, alias_map: Dict[str, List[str]], threshold: float = 0.74) -> Optional[MatchResult]:
    best: Optional[MatchResult] = None

    for canonical, aliases in alias_map.items():
        for alias in aliases:
            sub = _substring_score(query, alias)
            tok = _token_overlap_score(query, alias)

            score = max(sub, tok)

            if score >= threshold:
                if best is None or score > best.score:
                    best = MatchResult(
                        canonical=canonical,
                        alias=alias,
                        score=score,
                    )

    return best


ARTIST_ALIASES: Dict[str, List[str]] = {
    "Wojciech Fangor": [
        "wojciech fangor",
        "fangor",
        "fango",
        "fangohr",
        "van moor",
        "fugner",
        "fugnor",
        "woitschech fangor",
    ],
    "Wassily Kandinsky": [
        "wassily kandinsky",
        "kandinsky",
        "kandinski",
        "kandisky",
        "kandiski",
        "basilikum",
        "wassili kandinsky",
    ],
    "Bridget Riley": [
        "bridget riley",
        "bridget",
        "brigitte",
        "britta",
        "riley",
        "reilly",
        "reil",
        "dryly",
        "dreiling",
        "bridge dry",
        "brille dry",
        "bridget dry",
    ],
    "Victor Vasarely": [
        "victor vasarely",
        "vasarely",
        "vasareli",
        "vasarelli",
        "basarely",
        "basali",
        "bazali",
        "bazarew",
        "bazarev",
        "vasarew",
        "vasarev",
    ],
    "Julian Stanczak": [
        "julian stanczak",
        "stanczak",
        "stansak",
        "stanzak",
    ],
    "Margaret Wenstrup": [
        "margaret wenstrup",
        "wenstrup",
        "wenstrub",
        "wenstrupf",
        "wenstrupp",
        "benstrup",
    ],
    "Edna Andrade": [
        "edna andrade",
        "andrade",
    ],
}

ARTWORK_ALIASES: Dict[str, List[str]] = {
    "Im schwarzen kreis": [
        "im schwarzen kreis",
        "den schwarzen kreis",
        "der schwarze kreis",
        "schwarzen kreis",
    ],
    "Boglar i": [
        "boglar i",
        "boglar 1",
        "boglar eins",
        "bogolar i",
        "bogolar eins",
        "bogolar",
        "buglar",
        "bukla",
        "bogler",
        "buckenhahe eins",
    ],
    "Klepsydra 1": [
        "klepsydra 1",
        "klepsydra eins",
        "clepsydra",
        "klepsidra",
    ],
    "Kreisel": [
        "kreisel",
        "kreiser",
    ],
    "Yabla": [
        "yabla",
        "jabla",
        "yabla",
    ],
    "Shih-Li": [
        "shih-li",
        "shih li",
        "shi li",
        "schi li",
    ],
    "Zittern": [
        "zittern",
    ],
    "B13": [
        "b13",
        "b 13",
        "b dreizehn",
        "bee 13",
        "be 13",
        "bi 13",
    ],
    "B15": [
        "b15",
        "b 15",
        "b fünfzehn",
        "b funfzehn",
    ],
    "E37": [
        "e37",
        "e 37",
        "i 37",
    ],
    "E47": [
        "e47",
        "e 47",
        "i 47",
    ],
    "Spätes Leuchten": [
        "spätes leuchten",
        "spaetes leuchten",
        "spates leuchten",
    ],
    "Abstoßende anziehung": [
        "abstoßende anziehung",
        "abstossende anziehung",
    ],
    "Flüchtige Bewegung": [
        "flüchtige bewegung",
        "fluchtige bewegung",
        "fluechtige bewegung",
    ],
    "4-64": [
        "4-64",
        "4 64",
        "4.64",
        "farbbewegung",
    ],
}

GENERAL_ALIASES: Dict[str, List[str]] = {
    "op-art": [
        "op-art",
        "op art",
    ],
    "space age": [
        "space age",
        "space-age",
    ],
    "vierte dimension": [
        "vierte dimension",
    ],
}


def find_artist(query: str) -> Optional[MatchResult]:
    return _best_match(query, ARTIST_ALIASES, threshold=0.74)


def find_artwork(query: str) -> Optional[MatchResult]:
    return _best_match(query, ARTWORK_ALIASES, threshold=0.74)


def find_general_topic(query: str) -> Optional[MatchResult]:
    return _best_match(query, GENERAL_ALIASES, threshold=0.74)