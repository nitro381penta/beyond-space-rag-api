import re


def normalize_for_tts(text: str) -> str:
    if not text:
        return text

    spoken = text

    # Titel mit römischen Ziffern für natürlichere Ausgabe
    spoken = re.sub(r"\bBoglar I\b", "Boglar eins", spoken)
    spoken = re.sub(r"\bVegaviv II\b", "Vegaviv zwei", spoken)
    spoken = re.sub(r"\bKlepsydra 1\b", "Klepsydra eins", spoken)

    # B-/E-Werke natürlicher sprechen
    spoken = re.sub(r"\bB13\b", "B 13", spoken)
    spoken = re.sub(r"\bB15\b", "B 15", spoken)
    spoken = re.sub(r"\bE37\b", "E 37", spoken)
    spoken = re.sub(r"\bE47\b", "E 47", spoken)

    return spoken


def beautify_query_for_display(raw_text: str, normalized_query: str) -> str:
    if not normalized_query:
        return raw_text or ""

    q = normalized_query.strip()

    # Frageformulierungen glätten
    q = re.sub(r"\bvan lebte\b", "wann lebte", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwan lebte\b", "wann lebte", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwan wurde\b", "wann wurde", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwan erschien\b", "wann erschien", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwan entstand\b", "wann entstand", q, flags=re.IGNORECASE)

    # Künstlernamen
    replacements = [
        (r"\bbridget riley\b", "Bridget Riley"),
        (r"\bbritta reilly\b", "Bridget Riley"),
        (r"\bbritta riley\b", "Bridget Riley"),
        (r"\bvictor vasarely\b", "Victor Vasarely"),
        (r"\bwojciech fangor\b", "Wojciech Fangor"),
        (r"\bmargaret wenstrup\b", "Margaret Wenstrup"),
        (r"\bwassily kandinsky\b", "Wassily Kandinsky"),

        # Werktitel
        (r"\byabla\b", "Yabla"),
        (r"\bboglar i\b", "Boglar I"),
        (r"\bim schwarzen kreis\b", "Im schwarzen Kreis"),
        (r"\bklepsydra 1\b", "Klepsydra 1"),
        (r"\bshih li\b", "Shih-Li"),
        (r"\bkreisel\b", "Kreisel"),
        (r"\bzittern\b", "Zittern"),

        # Codes
        (r"\bb13\b", "B13"),
        (r"\bb15\b", "B15"),
        (r"\be37\b", "E37"),
        (r"\be47\b", "E47"),
    ]

    for pattern, repl in replacements:
        q = re.sub(pattern, repl, q, flags=re.IGNORECASE)

    # Häufige Werkfrage-Formulierungen hübscher machen
    q = re.sub(r"\bwann erschien das werk ([^?]+)\b", r"Wann erschien das Werk \1", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwann entstand das werk ([^?]+)\b", r"Wann entstand das Werk \1", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwann wurde ([^?]+) gemalt\b", r"Wann wurde \1 gemalt", q, flags=re.IGNORECASE)
    q = re.sub(r"\bwann lebte ([^?]+)\b", r"Wann lebte \1", q, flags=re.IGNORECASE)

    q = q.strip()

    if q:
        q = q[0].upper() + q[1:]

    if not q.endswith("?"):
        q += "?"

    return q