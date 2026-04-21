import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List, Optional


def _ascii(text: str) -> str:
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    ).lower()


def _normalize(text: str) -> str:
    text = _ascii(text)
    text = text.replace("ß", "ss")
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _compact(text: str) -> str:
    return re.sub(r"\s+", "", _normalize(text))


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


@dataclass
class MatchCandidate:
    canonical: str
    score: float
    matched_variant: Optional[str] = None


ARTISTS = {
    "wojciech fangor": [
        "wojciech fangor", "fangor", "fango", "fangohr", "vangor",
        "van moor", "fugner", "fugnor", "fugner", "woitschech fangor"
    ],
    "wassily kandinsky": [
        "wassily kandinsky", "kandinsky", "kandinski", "kandisky",
        "kandiski", "basilikum", "wassili kandinsky"
    ],
    "bridget riley": [
        "bridget riley", "bridget", "brigitte", "britta", "riley",
        "reilly", "reil", "dryly", "dreiling", "bridge dryly",
        "britta dryly", "bridge to try me"
    ],
    "victor vasarely": [
        "victor vasarely", "vasarely", "vasareli", "vasarelli",
        "basarely", "bazarew", "wasarely", "vasarin", "bazarev"
    ],
    "julian stanczak": [
        "julian stanczak", "stanczak", "stancak", "stanchak"
    ],
    "margaret wenstrup": [
        "margaret wenstrup", "wenstrup", "wenstrub", "wenstrupf",
        "wenstrüp", "benstrup"
    ],
    "edna andrade": [
        "edna andrade", "andrade"
    ],
}

ARTWORKS = {
    "im schwarzen kreis": [
        "im schwarzen kreis", "den schwarzen kreis", "der schwarze kreis",
        "schwarzen kreis"
    ],
    "boglar i": [
        "boglar i", "boglar 1", "boglar eins", "buglar", "bukla", "bogler"
    ],
    "klepsydra 1": [
        "klepsydra 1", "klepsydra eins", "clepsydra", "klepsidra"
    ],
    "kreisel": [
        "kreisel", "wenstrup kreisel"
    ],
    "yabla": [
        "yabla", "jabla", "jablo"
    ],
    "shih-li": [
        "shih-li", "shih li", "shi li", "schi li"
    ],
    "zittern": [
        "zittern"
    ],
    "b13": [
        "b13", "b 13", "b dreizehn", "bee 13", "be 13", "bi 13"
    ],
    "b15": [
        "b15", "b 15", "b fünfzehn", "b funfzehn"
    ],
    "e37": [
        "e37", "e 37", "i 37"
    ],
    "e47": [
        "e47", "e 47", "i 47"
    ],
    "spätes leuchten": [
        "spätes leuchten", "spaetes leuchten", "spates leuchten"
    ],
    "abstoßende anziehung": [
        "abstoßende anziehung", "abstossende anziehung"
    ],
    "flüchtige bewegung": [
        "flüchtige bewegung", "fluechtige bewegung", "fluchtige bewegung"
    ],
    "4-64": [
        "4-64", "4 64", "4.64", "farbbewegung"
    ],
}

GENERAL = {
    "op-art": ["op-art", "op art"],
    "space age": ["space age", "space-age"],
    "vierte dimension": ["vierte dimension"],
}


def _best_match(text: str, candidates: dict[str, list[str]], threshold: float = 0.72) -> Optional[MatchCandidate]:
    text_norm = _normalize(text)
    text_compact = _compact(text)

    best: Optional[MatchCandidate] = None

    for canonical, variants in candidates.items():
        all_forms = [canonical] + variants
        for variant in all_forms:
            variant_norm = _normalize(variant)
            variant_compact = _compact(variant)

            score = 0.0

            if variant_norm and variant_norm in text_norm:
                score = 1.0
            elif variant_compact and variant_compact in text_compact:
                score = 0.98
            else:
                score = max(
                    _similarity(text_norm, variant_norm),
                    _similarity(text_compact, variant_compact),
                )

            if best is None or score > best.score:
                best = MatchCandidate(
                    canonical=canonical,
                    score=score,
                    matched_variant=variant,
                )

    if best and best.score >= threshold:
        return best
    return None


def find_artist(text: str) -> Optional[MatchCandidate]:
    return _best_match(text, ARTISTS, threshold=0.70)


def find_artwork(text: str) -> Optional[MatchCandidate]:
    return _best_match(text, ARTWORKS, threshold=0.72)


def find_general_topic(text: str) -> Optional[MatchCandidate]:
    return _best_match(text, GENERAL, threshold=0.78)