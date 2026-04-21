import re
import unicodedata


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )


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

    spoken = re.sub(r"\bShih-Li\b", "Schih Li", spoken)
    spoken = re.sub(r"\bYabla\b", "Jabla", spoken)

    spoken = re.sub(r"\bum\s+1923\b", "ungefähr 1923", spoken)

    spoken = re.sub(r"\s+", " ", spoken).strip()
    return spoken


def _fix_title_casing(text: str) -> str:
    text = re.sub(r"\bim schwarzen kreis\b", "Im schwarzen Kreis", text, flags=re.IGNORECASE)
    text = re.sub(r"\bboglar i\b", "Boglar I", text, flags=re.IGNORECASE)
    text = re.sub(r"\byabla\b", "Yabla", text, flags=re.IGNORECASE)
    text = re.sub(r"\bbridget riley\b", "Bridget Riley", text, flags=re.IGNORECASE)
    text = re.sub(r"\bvictor vasarely\b", "Victor Vasarely", text, flags=re.IGNORECASE)
    text = re.sub(r"\bwojciech fangor\b", "Wojciech Fangor", text, flags=re.IGNORECASE)
    text = re.sub(r"\bmargaret wenstrup\b", "Margaret Wenstrup", text, flags=re.IGNORECASE)
    text = re.sub(r"\bwassily kandinsky\b", "Wassily Kandinsky", text, flags=re.IGNORECASE)
    text = re.sub(r"\bkandinsky\b", "Kandinsky", text, flags=re.IGNORECASE)
    text = re.sub(r"\bjulian stanczak\b", "Julian Stanczak", text, flags=re.IGNORECASE)
    text = re.sub(r"\bb13\b", "B13", text, flags=re.IGNORECASE)
    text = re.sub(r"\bb15\b", "B15", text, flags=re.IGNORECASE)
    text = re.sub(r"\be37\b", "E37", text, flags=re.IGNORECASE)
    text = re.sub(r"\be47\b", "E47", text, flags=re.IGNORECASE)
    text = re.sub(r"\bklepsydra 1\b", "Klepsydra 1", text, flags=re.IGNORECASE)
    text = re.sub(r"\bshih-li\b", "Shih-Li", text, flags=re.IGNORECASE)
    text = re.sub(r"\bkreisel\b", "Kreisel", text, flags=re.IGNORECASE)
    text = re.sub(r"\bzittern\b", "Zittern", text, flags=re.IGNORECASE)
    text = re.sub(r"\bop-art\b", "Op-Art", text, flags=re.IGNORECASE)
    text = re.sub(r"\bspace age\b", "Space Age", text, flags=re.IGNORECASE)
    return text


def _capitalize_first(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def beautify_query_for_display(raw_text: str, normalized_query: str) -> str:
    source = normalized_query if normalized_query else raw_text
    if not source:
        return ""

    q = source.strip().lower()
    q = _strip_accents(q)
    q = q.replace("ß", "ss")
    q = re.sub(r"\s+", " ", q).strip()
    q = re.sub(r"[?!.,;:]+$", "", q)

    q = re.sub(r"^schien\b", "wann entstand", q)
    q = re.sub(r"^erschien\b", "wann entstand", q)
    q = re.sub(r"^wer war\b", "wer ist", q)
    q = re.sub(r"^wer hat\b", "von wem ist", q)

    q = re.sub(r"^dann lebt die (.+)$", r"wann lebte \1", q)
    q = re.sub(r"^dann lebt (.+)$", r"wann lebte \1", q)
    q = re.sub(r"^liebte (.+)$", r"wann lebte \1", q)
    q = re.sub(r"^wann liebte (.+)$", r"wann lebte \1", q)

    q = re.sub(r"\bbogolar\b", "boglar i", q)
    q = re.sub(r"\bbogolar i\b", "boglar i", q)

    q = re.sub(
        r"^wann wurde im schwarzen kreis von (.+) gemalt$",
        r"wann wurde das werk im schwarzen kreis von \1 gemalt",
        q,
        flags=re.IGNORECASE,
    )

    q = re.sub(r"\s+", " ", q).strip()
    q = _fix_title_casing(q)
    q = _capitalize_first(q)

    if not q.endswith("?"):
        q += "?"

    return q