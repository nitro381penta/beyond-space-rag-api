import re


def normalize_for_tts(text: str) -> str:
    if not text:
        return text

    spoken = text

    # Künstlernamen natürlicher sprechen
    spoken = re.sub(r"\bWojciech\b", "Woitschech", spoken)
    spoken = re.sub(r"\bVasarely\b", "Vasarely", spoken)
    spoken = re.sub(r"\bBridget Riley\b", "Bridget Riley", spoken)
    spoken = re.sub(r"\bWassily Kandinsky\b", "Wassily Kandinsky", spoken)
    spoken = re.sub(r"\bMargaret Wenstrup\b", "Margaret Wenstrup", spoken)

    # Titel mit römischen Ziffern für natürlichere Ausgabe
    spoken = re.sub(r"\bBoglar I\b", "Boglar eins", spoken)
    spoken = re.sub(r"\bVegaviv II\b", "Vegaviv zwei", spoken)
    spoken = re.sub(r"\bKlepsydra 1\b", "Klepsydra eins", spoken)

    # B-/E-Werke natürlicher sprechen
    spoken = re.sub(r"\bB13\b", "B 13", spoken)
    spoken = re.sub(r"\bB15\b", "B 15", spoken)
    spoken = re.sub(r"\bE37\b", "E 37", spoken)
    spoken = re.sub(r"\bE47\b", "E 47", spoken)

    # Jahresangaben etwas flüssiger
    spoken = re.sub(r"\bum\s+1923\b", "ungefähr 1923", spoken)

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

    q = normalized_query.strip().lower()

    # Frageanfänge glätten
    q = re.sub(r"\bvan\b", "wann", q)
    q = re.sub(r"\bwan\b", "wann", q)

    # Frageformulierungen vereinheitlichen
    q = re.sub(r"\bwann ist (.+?) erschienen\b", r"wann entstand \1", q)
    q = re.sub(r"\bwann erschien (.+?)\b", r"wann entstand \1", q)

    # Häufige STT-Fehler für Namen
    q = re.sub(r"\bbritta reilly\b", "bridget riley", q)
    q = re.sub(r"\bbritta riley\b", "bridget riley", q)
    q = re.sub(r"\breilly\b", "riley", q)

    q = re.sub(r"\bbasarili\b", "vasarely", q)
    q = re.sub(r"\bvasarili\b", "vasarely", q)
    q = re.sub(r"\bvasarelli\b", "vasarely", q)

    q = re.sub(r"\bfango\b", "fangor", q)
    q = re.sub(r"\bvojtech\b", "wojciech", q)
    q = re.sub(r"\bvojte[ch]?\b", "wojciech", q)

    q = re.sub(r"\bmargret\b", "margaret", q)
    q = re.sub(r"\bwenstrub\b", "wenstrup", q)
    q = re.sub(r"\bwenstrüp\b", "wenstrup", q)
    q = re.sub(r"\bbenstrup\b", "wenstrup", q)

    # Werktitel / STT-Fehler
    q = re.sub(r"\bjabla\b", "yabla", q)
    q = re.sub(r"\bjableh\b", "yabla", q)
    q = re.sub(r"\bjabloh\b", "yabla", q)
    q = re.sub(r"\bjablo\b", "yabla", q)

    q = re.sub(r"\bbukla\b", "boglar", q)
    q = re.sub(r"\bbogla\b", "boglar", q)
    q = re.sub(r"\bboklar\b", "boglar", q)
    q = re.sub(r"\bboglár\b", "boglar", q)
    q = re.sub(r"\bbugla\b", "boglar", q)
    q = re.sub(r"\bbugla eins\b", "boglar i", q)
    q = re.sub(r"\bbugla 1\b", "boglar i", q)

    q = re.sub(r"\bboglar eins\b", "boglar i", q)
    q = re.sub(r"\bboglar 1\b", "boglar i", q)
    q = re.sub(r"\bboklar eins\b", "boglar i", q)
    q = re.sub(r"\bboklar 1\b", "boglar i", q)
    q = re.sub(r"\bbukla eins\b", "boglar i", q)
    q = re.sub(r"\bbukla 1\b", "boglar i", q)

    q = re.sub(r"\bin den schwarzen kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bder schwarze kreis\b", "im schwarzen kreis", q)

    # Codes hübsch lassen
    q = re.sub(r"\bb\s*[\.\-]?\s*13\b", "b13", q)
    q = re.sub(r"\bb\s*[\.\-]?\s*15\b", "b15", q)
    q = re.sub(r"\be\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\be\s*[\.\-]?\s*47\b", "e47", q)

    # Schöne Schreibweisen
    replacements = [
        (r"\bbridget riley\b", "Bridget Riley"),
        (r"\bvictor vasarely\b", "Victor Vasarely"),
        (r"\bvasarely\b", "Vasarely"),
        (r"\bwojciech fangor\b", "Wojciech Fangor"),
        (r"\bmargaret wenstrup\b", "Margaret Wenstrup"),
        (r"\bwassily kandinsky\b", "Wassily Kandinsky"),
        (r"\bkandinsky\b", "Kandinsky"),
        (r"\byabla\b", "Yabla"),
        (r"\bboglar i\b", "Boglar I"),
        (r"\bim schwarzen kreis\b", "Im schwarzen Kreis"),
        (r"\bklepsydra 1\b", "Klepsydra 1"),
        (r"\bshih li\b", "Shih-Li"),
        (r"\bkreisel\b", "Kreisel"),
        (r"\bzittern\b", "Zittern"),
        (r"\bb13\b", "B13"),
        (r"\bb15\b", "B15"),
        (r"\be37\b", "E37"),
        (r"\be47\b", "E47"),
    ]

    for pattern, repl in replacements:
        q = re.sub(pattern, repl, q, flags=re.IGNORECASE)

    # Frageformulierungen hübscher machen
    q = re.sub(
        r"\bwann entstand das werk ([^?]+)\b",
        r"Wann entstand das Werk \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"\bwann entstand ([^?]+)\b",
        r"Wann entstand \1",
        q,
        flags=re.IGNORECASE,
    )
    q = re.sub(
        r"\bwann wurde ([^?]+) gemalt\b",
        r"Wann wurde \1 gemalt",
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
        r"\bwas bedeutete die vierte dimension für ([^?]+)\b",
        r"Was bedeutete die vierte Dimension für \1",
        q,
        flags=re.IGNORECASE,
    )

    q = re.sub(r"\s+", " ", q).strip()

    q = _fix_title_casing(q)
    q = _capitalize_first(q)

    if not q.endswith("?"):
        q += "?"

    return q


def _capitalize_first(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


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
    text = re.sub(r"\bb13\b", "B13", text, flags=re.IGNORECASE)
    text = re.sub(r"\bb15\b", "B15", text, flags=re.IGNORECASE)
    text = re.sub(r"\be37\b", "E37", text, flags=re.IGNORECASE)
    text = re.sub(r"\be47\b", "E47", text, flags=re.IGNORECASE)
    text = re.sub(r"\bklepsydra 1\b", "Klepsydra 1", text, flags=re.IGNORECASE)
    text = re.sub(r"\bshih li\b", "Shih-Li", text, flags=re.IGNORECASE)
    text = re.sub(r"\bkreisel\b", "Kreisel", text, flags=re.IGNORECASE)
    text = re.sub(r"\bzittern\b", "Zittern", text, flags=re.IGNORECASE)
    return text