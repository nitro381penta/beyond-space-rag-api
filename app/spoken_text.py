import re
import unicodedata


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )


def _capitalize_first(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def _fix_title_casing(text: str) -> str:
    if not text:
        return text

    replacements = [
        (r"\bbridget riley\b", "Bridget Riley"),
        (r"\bvictor vasarely\b", "Victor Vasarely"),
        (r"\bwojciech fangor\b", "Wojciech Fangor"),
        (r"\bwassily kandinsky\b", "Wassily Kandinsky"),
        (r"\bmargaret wenstrup\b", "Margaret Wenstrup"),
        (r"\bjulian stanczak\b", "Julian Stanczak"),
        (r"\bedna andrade\b", "Edna Andrade"),

        (r"\bim schwarzen kreis\b", "Im schwarzen Kreis"),
        (r"\bboglar i\b", "Boglar I"),
        (r"\bklepsydra 1\b", "Klepsydra 1"),
        (r"\bshih-li\b", "Shih-Li"),
        (r"\byabla\b", "Yabla"),
        (r"\bkreisel\b", "Kreisel"),
        (r"\bzittern\b", "Zittern"),

        (r"\bb13\b", "B13"),
        (r"\bb15\b", "B15"),
        (r"\be37\b", "E37"),
        (r"\be47\b", "E47"),

        (r"\bop-art\b", "Op-Art"),
        (r"\bspace age\b", "Space Age"),
    ]

    out = text
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)

    return out


def normalize_for_tts(text: str) -> str:
    if not text:
        return text

    spoken = text

    # Künstlernamen für natürlichere deutsche Aussprache
    spoken = re.sub(r"\bWojciech\b", "Woitschech", spoken)
    spoken = re.sub(r"\bWassily\b", "Wassili", spoken)
    spoken = re.sub(r"\bKandinsky\b", "Kandinski", spoken)
    spoken = re.sub(r"\bVasarely\b", "Wasarely", spoken)
    spoken = re.sub(r"\bJulian Stanczak\b", "Julian Stansak", spoken)

    # Werke natürlicher sprechen
    spoken = re.sub(r"\bBoglar I\b", "Boglar eins", spoken)
    spoken = re.sub(r"\bKlepsydra 1\b", "Klepsydra eins", spoken)

    # B-/E-Werke natürlicher sprechen
    spoken = re.sub(r"\bB13\b", "B 13", spoken)
    spoken = re.sub(r"\bB15\b", "B 15", spoken)
    spoken = re.sub(r"\bE37\b", "E 37", spoken)
    spoken = re.sub(r"\bE47\b", "E 47", spoken)

    # Titel
    spoken = re.sub(r"\bShih-Li\b", "Schih Li", spoken)
    spoken = re.sub(r"\bYabla\b", "Jabla", spoken)

    # Zahlen / Jahre etwas natürlicher
    spoken = re.sub(r"\bum 1923\b", "ungefähr 1923", spoken)
    spoken = re.sub(r"\bca\. 1923\b", "ungefähr 1923", spoken)

    # typografische Bereinigung
    spoken = spoken.replace("„", '"').replace("“", '"')
    spoken = spoken.replace("–", "-").replace("—", "-")
    spoken = re.sub(r"\s+", " ", spoken).strip()

    return spoken


def beautify_query_for_display(
    raw_text: str,
    normalized_query: str,
    repaired_query: str = "",
) -> str:
    # Priorität: repaired > normalized > raw
    source = repaired_query or normalized_query or raw_text
    if not source:
        return ""

    q = source.strip().lower()
    q = _strip_accents(q)
    q = q.replace("ß", "ss")
    q = re.sub(r"\s+", " ", q).strip()
    q = re.sub(r"[?!.,;:]+$", "", q)

    # Satzanfänge / Frageformen glätten
    q = re.sub(r"^wer hat\b", "von wem ist", q)
    q = re.sub(r"^wer malte\b", "von wem ist", q)
    q = re.sub(r"^dann lebte\b", "wann lebte", q)
    q = re.sub(r"^dann lebt\b", "wann lebte", q)
    q = re.sub(r"^liebte\b", "wann lebte", q)
    q = re.sub(r"^lebt\b", "wann lebte", q)
    q = re.sub(r"^schien\b", "wann entstand", q)
    q = re.sub(r"^erschien\b", "wann entstand", q)

    # Bridget-Riley-Sonderfälle
    q = re.sub(r"\bbridge dryly\b", "bridget riley", q)
    q = re.sub(r"\bbridge riley\b", "bridget riley", q)
    q = re.sub(r"\bbritta dryly\b", "bridget riley", q)
    q = re.sub(r"\bbridget dryly\b", "bridget riley", q)
    q = re.sub(r"\bdreiling\b", "riley", q)
    q = re.sub(r"\bdryly\b", "riley", q)
    q = re.sub(r"\breilly\b", "riley", q)
    q = re.sub(r"\breil\b", "riley", q)
    q = re.sub(r"\bbrigitte\b", "bridget", q)
    q = re.sub(r"\bbritta\b", "bridget", q)

    # weitere Namen
    q = re.sub(r"\bbazarew\b", "vasarely", q)
    q = re.sub(r"\bbazarev\b", "vasarely", q)
    q = re.sub(r"\bvasareli\b", "vasarely", q)
    q = re.sub(r"\bvasarelli\b", "vasarely", q)
    q = re.sub(r"\bbasarely\b", "vasarely", q)
    q = re.sub(r"\bwasarely\b", "vasarely", q)

    q = re.sub(r"\bbasilikum\b", "kandinsky", q)
    q = re.sub(r"\bkandinski\b", "kandinsky", q)
    q = re.sub(r"\bkandisky\b", "kandinsky", q)

    q = re.sub(r"\bvan moor\b", "fangor", q)
    q = re.sub(r"\bfugner\b", "fangor", q)
    q = re.sub(r"\bfugnor\b", "fangor", q)

    # Werke
    q = re.sub(r"\bb dreizehn\b", "b13", q)
    q = re.sub(r"\bb funfzehn\b", "b15", q)
    q = re.sub(r"\bb fünfzehn\b", "b15", q)
    q = re.sub(r"\be 37\b", "e37", q)
    q = re.sub(r"\be 47\b", "e47", q)
    q = re.sub(r"\bi 37\b", "e37", q)
    q = re.sub(r"\bi 47\b", "e47", q)

    q = re.sub(r"\bden schwarzen kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bder schwarze kreis\b", "im schwarzen kreis", q)

    # hübsche Form
    q = re.sub(
        r"\bwann entstand das werk ([^?]+)\b",
        r"Wann entstand das Werk \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"\bwann wurde das werk ([^?]+) gemalt\b",
        r"Wann wurde das Werk \1 gemalt",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"\bwann wurde ([^?]+) geboren\b",
        r"Wann wurde \1 geboren",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"\bwann lebte ([^?]+)\b",
        r"Wann lebte \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"\bvon wem ist ([^?]+)\b",
        r"Von wem ist \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"\bwas bedeutete die vierte dimension fur ([^?]+)\b",
        r"Was bedeutete die vierte Dimension für \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"\bwas bedeutete die vierte dimension fuer ([^?]+)\b",
        r"Was bedeutete die vierte Dimension für \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"\bwie kann man op-art definieren\b",
        r"Wie kann man Op-Art definieren",
        q,
        flags=re.IGNORECASE,
    )

    q = re.sub(r"\s+", " ", q).strip()
    q = _fix_title_casing(q)
    q = _capitalize_first(q)

    if not q.endswith("?"):
        q += "?"

    return q