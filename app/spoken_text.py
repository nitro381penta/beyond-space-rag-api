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

    # Künstlernamen
    spoken = re.sub(r"\bWojciech\b", "Woitschech", spoken)
    spoken = re.sub(r"\bWassily\b", "Wassili", spoken)
    spoken = re.sub(r"\bKandinsky\b", "Kandinski", spoken)

    # Werktitel mit römischen Ziffern für natürlichere Ausgabe
    spoken = re.sub(r"\bBoglar I\b", "Boglar eins", spoken)
    spoken = re.sub(r"\bVegaviv II\b", "Vegaviv zwei", spoken)
    spoken = re.sub(r"\bKlepsydra 1\b", "Klepsydra eins", spoken)

    # B-/E-Werke natürlicher sprechen
    spoken = re.sub(r"\bB13\b", "B 13", spoken)
    spoken = re.sub(r"\bB15\b", "B 15", spoken)
    spoken = re.sub(r"\bE37\b", "E 37", spoken)
    spoken = re.sub(r"\bE47\b", "E 47", spoken)

    # Titel
    spoken = re.sub(r"\bShih-Li\b", "Schih Li", spoken)
    spoken = re.sub(r"\bYabla\b", "Jabla", spoken)

    # Jahresangaben
    spoken = re.sub(r"\bum\s+1923\b", "ungefähr 1923", spoken)

    return spoken


def beautify_query_for_display(raw_text: str, normalized_query: str) -> str:
    source = normalized_query if normalized_query else raw_text
    if not source:
        return ""

    q = source.strip().lower()
    q = _strip_accents(q)
    q = q.replace("ß", "ss")
    q = re.sub(r"\s+", " ", q).strip()
    q = re.sub(r"[?!.,;:]+$", "", q)

    # Häufige falsche Starts / Fragmente
    q = re.sub(r"^schien\b", "wann entstand", q)
    q = re.sub(r"^erschien\b", "wann entstand", q)
    q = re.sub(r"^wer war\b", "wer ist", q)
    q = re.sub(r"^wer hat\b", "wer malte", q)

    # Künstlernamen
    q = re.sub(r"\bviktor\b", "victor", q)

    q = re.sub(r"\bbasarin\b", "vasarely", q)
    q = re.sub(r"\bvasarin\b", "vasarely", q)
    q = re.sub(r"\bvasareli\b", "vasarely", q)
    q = re.sub(r"\bvasarelli\b", "vasarely", q)
    q = re.sub(r"\bvasaraly\b", "vasarely", q)
    q = re.sub(r"\bbasarely\b", "vasarely", q)
    q = re.sub(r"\bwasarely\b", "vasarely", q)
    q = re.sub(r"\bwasareli\b", "vasarely", q)
    q = re.sub(r"\bwasaweli\b", "vasarely", q)

    q = re.sub(r"\bfango\b", "fangor", q)
    q = re.sub(r"\bvojtech\b", "wojciech", q)
    q = re.sub(r"\bvojteh\b", "wojciech", q)
    q = re.sub(r"\bvojtec\b", "wojciech", q)

    q = re.sub(r"\bbrigitte\b", "bridget", q)
    q = re.sub(r"\bbritta\b", "bridget", q)
    q = re.sub(r"\bbridge\b", "bridget", q)
    q = re.sub(r"\bbridgit\b", "bridget", q)
    q = re.sub(r"\bbridgett\b", "bridget", q)

    q = re.sub(r"\breilly\b", "riley", q)
    q = re.sub(r"\breil\b", "riley", q)
    q = re.sub(r"\breill\b", "riley", q)
    q = re.sub(r"\bdryly\b", "riley", q)
    q = re.sub(r"\bdraily\b", "riley", q)
    q = re.sub(r"\bdreiling\b", "riley", q)
    q = re.sub(r"\bdreilin\b", "riley", q)

    q = re.sub(r"\bbridget reil\b", "bridget riley", q)
    q = re.sub(r"\bbridget reilly\b", "bridget riley", q)
    q = re.sub(r"\bbridget rail\b", "bridget riley", q)
    q = re.sub(r"\bbridget dryly\b", "bridget riley", q)
    q = re.sub(r"\bbridget draily\b", "bridget riley", q)
    q = re.sub(r"\bbridget dreiling\b", "bridget riley", q)
    q = re.sub(r"\bbritta riley\b", "bridget riley", q)
    q = re.sub(r"\bbritta reil\b", "bridget riley", q)
    q = re.sub(r"\bbritta dreiling\b", "bridget riley", q)

    q = re.sub(r"\bmargret\b", "margaret", q)
    q = re.sub(r"\bwenstrub\b", "wenstrup", q)
    q = re.sub(r"\bwenstrupp\b", "wenstrup", q)
    q = re.sub(r"\bwenstrupf\b", "wenstrup", q)

    q = re.sub(r"\bkandinski\b", "kandinsky", q)
    q = re.sub(r"\bkandisky\b", "kandinsky", q)
    q = re.sub(r"\bwassili\b", "wassily", q)
    q = re.sub(r"\bwasili\b", "wassily", q)

    # Extreme Sonderfälle aus STT
    q = re.sub(r"\bwir haben abgetrocknet\b", "wer ist bridget riley", q)
    q = re.sub(r"\bich bin liebti britta dreiling\b", "wann lebte bridget riley", q)
    q = re.sub(r"\bcant leave the bridge dryly\b", "wer ist bridget riley", q)
    q = re.sub(r"\bcan't leave the bridge dryly\b", "wer ist bridget riley", q)

    # Werktitel
    q = re.sub(r"\bjabla\b", "yabla", q)
    q = re.sub(r"\bjableh\b", "yabla", q)
    q = re.sub(r"\bjabloh\b", "yabla", q)
    q = re.sub(r"\bjablo\b", "yabla", q)

    q = re.sub(r"\bbukla\b", "boglar", q)
    q = re.sub(r"\bbugla\b", "boglar", q)
    q = re.sub(r"\bbuglar\b", "boglar", q)
    q = re.sub(r"\bbogla\b", "boglar", q)
    q = re.sub(r"\bboklar\b", "boglar", q)
    q = re.sub(r"\bbogler\b", "boglar", q)

    q = re.sub(r"\bboglar eins\b", "boglar i", q)
    q = re.sub(r"\bboglar 1\b", "boglar i", q)
    q = re.sub(r"\bboklar eins\b", "boglar i", q)
    q = re.sub(r"\bbukla eins\b", "boglar i", q)
    q = re.sub(r"\bbugla eins\b", "boglar i", q)
    q = re.sub(r"\bbuglar eins\b", "boglar i", q)

    q = re.sub(r"\bin den schwarzen kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bder schwarze kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bden schwarzen kreis\b", "im schwarzen kreis", q)

    q = re.sub(r"\bclepsydra\b", "klepsydra", q)
    q = re.sub(r"\bkleepsydra\b", "klepsydra", q)
    q = re.sub(r"\bklepsidra\b", "klepsydra", q)
    q = re.sub(r"\bklepsydra eins\b", "klepsydra 1", q)

    q = re.sub(r"\bshili\b", "shih-li", q)
    q = re.sub(r"\bschi li\b", "shih-li", q)
    q = re.sub(r"\bshi li\b", "shih-li", q)

    # Werkcodes
    q = re.sub(r"\bb\s*[\.\-]?\s*13\b", "b13", q)
    q = re.sub(r"\bb\s*[\.\-]?\s*15\b", "b15", q)
    q = re.sub(r"\be\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\be\s*[\.\-]?\s*47\b", "e47", q)
    q = re.sub(r"\bi\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\bi\s*[\.\-]?\s*47\b", "e47", q)

    # Frageformen glätten
    q = re.sub(r"\bwer malte\b", "von wem ist", q)
    q = re.sub(r"\bwer hat das werk ([a-z0-9\s\-]+) gemalt\b", r"von wem ist das Werk \1", q)
    q = re.sub(r"\bwer hat das ([a-z0-9\s\-]+) gemalt\b", r"von wem ist \1", q)
    q = re.sub(r"\bwer ist\b", "wer ist", q)
    q = re.sub(r"\bwann lebte\b", "wann lebte", q)
    q = re.sub(r"\bwann wurde\b", "wann wurde", q)
    q = re.sub(r"\bwann entstand\b", "wann entstand", q)
    q = re.sub(r"\bwas bedeutete\b", "was bedeutete", q)

    # Verbesserung der Schreibweise
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
        (r"\bshih-li\b", "Shih-Li"),
        (r"\bkreisel\b", "Kreisel"),
        (r"\bzittern\b", "Zittern"),
        (r"\bb13\b", "B13"),
        (r"\bb15\b", "B15"),
        (r"\be37\b", "E37"),
        (r"\be47\b", "E47"),
    ]

    for pattern, repl in replacements:
        q = re.sub(pattern, repl, q, flags=re.IGNORECASE)

    # Frageanfänge hübscher formulieren
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
        r"\bwer ist ([^?]+)\b",
        r"Wer ist \1",
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
    text = re.sub(r"\bshih-li\b", "Shih-Li", text, flags=re.IGNORECASE)
    text = re.sub(r"\bkreisel\b", "Kreisel", text, flags=re.IGNORECASE)
    text = re.sub(r"\bzittern\b", "Zittern", text, flags=re.IGNORECASE)
    return text