import re
import unicodedata


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )


DISPLAY_REPLACEMENTS = [
    (r"\bbridget riley\b", "Bridget Riley"),
    (r"\bvictor vasarely\b", "Victor Vasarely"),
    (r"\bwojciech fangor\b", "Wojciech Fangor"),
    (r"\bwassily kandinsky\b", "Wassily Kandinsky"),
    (r"\bjulian stanczak\b", "Julian Stanczak"),
    (r"\bmargaret wenstrup\b", "Margaret Wenstrup"),
    (r"\bedna andrade\b", "Edna Andrade"),

    (r"\bim schwarzen kreis\b", "Im schwarzen Kreis"),
    (r"\bboglar i\b", "Boglar I"),
    (r"\bklepsydra 1\b", "Klepsydra 1"),
    (r"\bkreisel\b", "Kreisel"),
    (r"\byabla\b", "Yabla"),
    (r"\bshih-li\b", "Shih-Li"),
    (r"\bzittern\b", "Zittern"),
    (r"\bspätes leuchten\b", "Spätes Leuchten"),
    (r"\babstoßende anziehung\b", "Abstoßende Anziehung"),
    (r"\bflüchtige bewegung\b", "Flüchtige Bewegung"),
    (r"\b4-64\b", "4-64"),

    (r"\bb13\b", "B13"),
    (r"\bb15\b", "B15"),
    (r"\be37\b", "E37"),
    (r"\be47\b", "E47"),

    (r"\bop-art\b", "Op-Art"),
    (r"\bspace age\b", "Space Age"),
    (r"\bvierte dimension\b", "vierte Dimension"),
]


def _apply_display_replacements(text: str) -> str:
    out = text
    for pattern, repl in DISPLAY_REPLACEMENTS:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def _capitalize_first(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def normalize_for_tts(text: str) -> str:
    if not text:
        return text

    spoken = text

    spoken = re.sub(r"\bWojciech\b", "Woitschech", spoken)
    spoken = re.sub(r"\bWassily\b", "Wassili", spoken)
    spoken = re.sub(r"\bKandinsky\b", "Kandinski", spoken)
    spoken = re.sub(r"\bVasarely\b", "Wasarely", spoken)
    spoken = re.sub(r"\bStanczak\b", "Stansak", spoken)

    spoken = re.sub(r"\bBoglar I\b", "Boglar eins", spoken)
    spoken = re.sub(r"\bKlepsydra 1\b", "Klepsydra eins", spoken)

    spoken = re.sub(r"\bB13\b", "B 13", spoken)
    spoken = re.sub(r"\bB15\b", "B 15", spoken)
    spoken = re.sub(r"\bE37\b", "E 37", spoken)
    spoken = re.sub(r"\bE47\b", "E 47", spoken)

    spoken = re.sub(r"\bYabla\b", "Jabla", spoken)
    spoken = re.sub(r"\bum 1923\b", "ungefähr 1923", spoken)

    spoken = re.sub(r"\s+", " ", spoken).strip()
    return spoken


def beautify_query_for_display(raw_text: str, repaired_text: str) -> str:
    source = repaired_text or raw_text or ""
    if not source:
        return ""

    q = source.strip()
    q = _strip_accents(q)
    q = q.replace("ß", "ss")

    q = re.sub(r"\s+", " ", q).strip()
    q = re.sub(r"[?!.,;:]+$", "", q)

    q = _apply_display_replacements(q)

    q = re.sub(r"\bdas werk\b", "das Werk", q, flags=re.IGNORECASE)
    q = re.sub(r"\bvon wem\b", "Von wem", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwer ist\b", "Wer ist", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwann lebte\b", "Wann lebte", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwann wurde\b", "Wann wurde", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwann entstand\b", "Wann entstand", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwas bedeutete\b", "Was bedeutete", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwie kann man\b", "Wie kann man", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwo wurde\b", "Wo wurde", q, flags=re.IGNORECASE)

    q = _capitalize_first(q)

    if not q.endswith("?"):
        q += "?"

    return q