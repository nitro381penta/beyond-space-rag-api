import re


def normalize_for_tts(text: str) -> str:
    if not text:
        return text

    spoken = text

    # Künstlernamen 
    spoken = re.sub(r"\bWojciech\b", "Woitschech", spoken)
    spoken = re.sub(r"\bWassily\b", "Wassili", spoken)
    spoken = re.sub(r"\bKandinsky\b", "Kandinski", spoken)

    # Werktitel
    spoken = re.sub(r"\bBoglar I\b", "Boglar eins", spoken)
    spoken = re.sub(r"\bVegaviv II\b", "Vegaviv zwei", spoken)
    spoken = re.sub(r"\bKlepsydra 1\b", "Klepsydra eins", spoken)
    spoken = re.sub(r"\bYabla\b", "Jabla", spoken)
    spoken = re.sub(r"\bB13\b", "B 13", spoken)
    spoken = re.sub(r"\bB15\b", "B 15", spoken)
    spoken = re.sub(r"\bE37\b", "E 37", spoken)
    spoken = re.sub(r"\bE47\b", "E 47", spoken)

    # Jahre
    spoken = re.sub(r"\bum 1923\b", "ungefähr 1923", spoken)
    spoken = re.sub(r"\baus dem jahr 1923\b", "aus dem Jahr 1923", spoken, flags=re.IGNORECASE)

    return spoken


def beautify_query_for_display(raw_text: str, normalized_query: str) -> str:
    if not normalized_query:
        q = (raw_text or "").strip()
        if not q:
            return ""
        q = _capitalize_first(q)
        if not q.endswith("?"):
            q += "?"
        return q

    q = normalized_query.strip()

    # Kanonische Schreibweisen
    q = _apply_pretty_replacements(q)

    # Typische Fragetemplates
    q = re.sub(
        r"^wann lebte ([^?]+)$",
        r"Wann lebte \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"^wer ist ([^?]+)$",
        r"Wer ist \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"^was bedeutete die vierte dimension fuer ([^?]+)$",
        r"Was bedeutete die vierte Dimension für \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"^was bedeutete die vierte dimension für ([^?]+)$",
        r"Was bedeutete die vierte Dimension für \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"^wann entstand das werk ([^?]+) von ([^?]+)$",
        r"Wann entstand das Werk \1 von \2",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"^wann entstand das werk ([^?]+)$",
        r"Wann entstand das Werk \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"^wann wurde ([^?]+) gemalt$",
        r"Wann wurde \1 gemalt",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"^aus welchem jahr ist ([^?]+)$",
        r"Aus welchem Jahr ist \1",
        q,
        flags=re.IGNORECASE,
    )

    # Falls der Normalizer nur einen Namen geliefert hat, dennoch lesbar machen
    q = _capitalize_first(q)
    q = _fix_title_casing(q)

    if not q.endswith("?"):
        q += "?"

    return q


def _apply_pretty_replacements(text: str) -> str:
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
        (r"\byabla\b", "Yabla"),
        (r"\bklepsydra 1\b", "Klepsydra 1"),
        (r"\bshih-li\b", "Shih-Li"),
        (r"\bshih li\b", "Shih-Li"),
        (r"\bzittern\b", "Zittern"),
        (r"\bkreisel\b", "Kreisel"),
        (r"\bb13\b", "B13"),
        (r"\bb15\b", "B15"),
        (r"\be37\b", "E37"),
        (r"\be47\b", "E47"),
        (r"\bfarbbewegung 4-64\b", "Farbbewegung 4-64"),
        (r"\babstossende anziehung\b", "Abstossende Anziehung"),
        (r"\bfluechtige bewegung\b", "Flüchtige Bewegung"),
        (r"\bspaetes leuchten\b", "Spätes Leuchten"),
    ]

    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    return text


def _capitalize_first(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def _fix_title_casing(text: str) -> str:
    fixes = [
        (r"\bIm schwarzen kreis\b", "Im schwarzen Kreis"),
        (r"\bBoglar i\b", "Boglar I"),
        (r"\bShih-li\b", "Shih-Li"),
        (r"\bB13\b", "B13"),
        (r"\bB15\b", "B15"),
        (r"\bE37\b", "E37"),
        (r"\bE47\b", "E47"),
        (r"\bKlepsydra 1\b", "Klepsydra 1"),
        (r"\bVictor Vasarely\b", "Victor Vasarely"),
        (r"\bBridget Riley\b", "Bridget Riley"),
        (r"\bWassily Kandinsky\b", "Wassily Kandinsky"),
        (r"\bWojciech Fangor\b", "Wojciech Fangor"),
        (r"\bMargaret Wenstrup\b", "Margaret Wenstrup"),
        (r"\bJulian Stanczak\b", "Julian Stanczak"),
        (r"\bEdna Andrade\b", "Edna Andrade"),
    ]

    for pattern, repl in fixes:
        text = re.sub(pattern, repl, text)

    # Deutsches "für"
    text = re.sub(r"\bfuer\b", "für", text, flags=re.IGNORECASE)

    return text