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

    spoken = text.strip()

    
    # KÜNSTLERNAMEN 
    
    spoken = re.sub(r"\bWojciech\b", "Woitschech", spoken)
    spoken = re.sub(r"\bWassily\b", "Wassili", spoken)
    spoken = re.sub(r"\bKandinsky\b", "Kandinski", spoken)

    # Vasarely 
    spoken = re.sub(r"\bVictor Vasarely\b", "Victor Vasarely", spoken)
    spoken = re.sub(r"\bBridget Riley\b", "Bridget Riley", spoken)
    spoken = re.sub(r"\bMargaret Wenstrup\b", "Margaret Wenstrup", spoken)
    spoken = re.sub(r"\bJulian Stanczak\b", "Julian Stanzak", spoken)
    spoken = re.sub(r"\bEdna Andrade\b", "Edna Andrade", spoken)

    
    # WERKTITEL
    
    spoken = re.sub(r"\bBoglar I\b", "Boglar eins", spoken)
    spoken = re.sub(r"\bVegaviv II\b", "Vegaviv zwei", spoken)
    spoken = re.sub(r"\bKlepsydra 1\b", "Klepsydra eins", spoken)

    # optional leicht natürlicher
    spoken = re.sub(r"\bShih-Li\b", "Schih Li", spoken)
    spoken = re.sub(r"\bYabla\b", "Jabla", spoken)

    
    # B-/E-WERKE
    
    spoken = re.sub(r"\bB13\b", "B 13", spoken)
    spoken = re.sub(r"\bB15\b", "B 15", spoken)
    spoken = re.sub(r"\bE37\b", "E 37", spoken)
    spoken = re.sub(r"\bE47\b", "E 47", spoken)

    
    # Formulierungen für natürlichere Ausgabe
    
    spoken = re.sub(r"\bum\s+1923\b", "ungefähr 1923", spoken)
    spoken = re.sub(r"\bum\s+(\d{4})\b", r"ungefähr \1", spoken)

    spoken = re.sub(
        r"\bIm Kontext steht auch:\s*aus dem Jahr (\d{4})\b",
        r"Im Kontext steht außerdem: aus dem Jahr \1",
        spoken,
        flags=re.IGNORECASE,
    )

    # doppelte Leerzeichen entfernen
    spoken = re.sub(r"\s+", " ", spoken).strip()
    return spoken


def beautify_query_for_display(raw_text: str, normalized_query: str) -> str:
    """
    Macht aus der rohen / normalisierten Frage eine hübsche Anzeige für das UI.
    Diese Funktion soll nur die Darstellung verbessern, nicht die Retrieval-Logik ändern.
    """
    source = (normalized_query or raw_text or "").strip()
    if not source:
        return ""

    q = _strip_accents(source.lower())
    q = re.sub(r"\s+", " ", q).strip()

    
    # Frageanfänge glätten
    
    q = re.sub(r"\bvan\b", "wann", q)
    q = re.sub(r"\bwan\b", "wann", q)

    # Frageformulierungen vereinheitlichen
    q = re.sub(r"\bwann ist (.+?) erschienen\b", r"wann entstand \1", q)
    q = re.sub(r"\bwann erschien (.+?)\b", r"wann entstand \1", q)

    
    # KÜNSTLERNAMEN korrigieren
    
    q = re.sub(r"\bbritta reilly\b", "bridget riley", q)
    q = re.sub(r"\bbritta riley\b", "bridget riley", q)
    q = re.sub(r"\bbridgit riley\b", "bridget riley", q)
    q = re.sub(r"\breilly\b", "riley", q)

    q = re.sub(r"\bbasarili\b", "vasarely", q)
    q = re.sub(r"\bvasarili\b", "vasarely", q)
    q = re.sub(r"\bvasarelli\b", "vasarely", q)
    q = re.sub(r"\bvasareli\b", "vasarely", q)
    q = re.sub(r"\bvasarin\b", "vasarely", q)
    q = re.sub(r"\bbasarin\b", "vasarely", q)
    q = re.sub(r"\bbasarely\b", "vasarely", q)
    q = re.sub(r"\bvictor basarin\b", "victor vasarely", q)

    q = re.sub(r"\bfango\b", "fangor", q)
    q = re.sub(r"\bvojtech\b", "wojciech", q)
    q = re.sub(r"\bvojteh\b", "wojciech", q)
    q = re.sub(r"\bvojtech fangor\b", "wojciech fangor", q)
    q = re.sub(r"\bvojte?ch\b", "wojciech", q)
    q = re.sub(r"\bvoitech\b", "wojciech", q)

    q = re.sub(r"\bmargret\b", "margaret", q)
    q = re.sub(r"\bwenstrub\b", "wenstrup", q)
    q = re.sub(r"\bwenstrupp\b", "wenstrup", q)
    q = re.sub(r"\bbenstrup\b", "wenstrup", q)

    q = re.sub(r"\bkandinski\b", "kandinsky", q)
    q = re.sub(r"\bkandinskiy\b", "kandinsky", q)

    
    # WERKTITEL / STT-FEHLER
    
    q = re.sub(r"\bjabla\b", "yabla", q)
    q = re.sub(r"\bjableh\b", "yabla", q)
    q = re.sub(r"\bjabloh\b", "yabla", q)
    q = re.sub(r"\bjablo\b", "yabla", q)
    q = re.sub(r"\byable\b", "yabla", q)

    q = re.sub(r"\bbukla\b", "boglar", q)
    q = re.sub(r"\bbugla\b", "boglar", q)
    q = re.sub(r"\bbuglar\b", "boglar", q)
    q = re.sub(r"\bbogla\b", "boglar", q)
    q = re.sub(r"\bboklar\b", "boglar", q)
    q = re.sub(r"\bbogler\b", "boglar", q)
    q = re.sub(r"\bbugler\b", "boglar", q)

    q = re.sub(r"\bbugla eins\b", "boglar i", q)
    q = re.sub(r"\bbugla 1\b", "boglar i", q)
    q = re.sub(r"\bbuglar eins\b", "boglar i", q)
    q = re.sub(r"\bbuglar 1\b", "boglar i", q)
    q = re.sub(r"\bboglar eins\b", "boglar i", q)
    q = re.sub(r"\bboglar 1\b", "boglar i", q)
    q = re.sub(r"\bboklar eins\b", "boglar i", q)
    q = re.sub(r"\bboklar 1\b", "boglar i", q)
    q = re.sub(r"\bbukla eins\b", "boglar i", q)
    q = re.sub(r"\bbukla 1\b", "boglar i", q)

    q = re.sub(r"\bin den schwarzen kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bden schwarzen kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bder schwarze kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bschwarzer kreis\b", "im schwarzen kreis", q)

    q = re.sub(r"\bclepsydra\b", "klepsydra", q)
    q = re.sub(r"\bklepsidra\b", "klepsydra", q)
    q = re.sub(r"\bklepsydra eins\b", "klepsydra 1", q)

    q = re.sub(r"\bshi li\b", "shih-li", q)
    q = re.sub(r"\bshih li\b", "shih-li", q)
    q = re.sub(r"\bshihli\b", "shih-li", q)

    
    # WERKCODES
    q = re.sub(r"\bb\s*[\.\-]?\s*13\b", "b13", q)
    q = re.sub(r"\bb\s*[\.\-]?\s*15\b", "b15", q)
    q = re.sub(r"\be\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\be\s*[\.\-]?\s*47\b", "e47", q)

    # STT verwechselt E mit I
    q = re.sub(r"\bi\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\bi\s*[\.\-]?\s*47\b", "e47", q)

    # weitere Fehler
    q = re.sub(r"\bbeat\s*\.?\s*13\b", "b13", q)
    q = re.sub(r"\bbeat\s*\.?\s*15\b", "b15", q)
    q = re.sub(r"\bbild\s*\.?\s*13\b", "b13", q)
    q = re.sub(r"\bbild\s*\.?\s*15\b", "b15", q)
    q = re.sub(r"\bbee\s*13\b", "b13", q)
    q = re.sub(r"\bbe\s*13\b", "b13", q)
    q = re.sub(r"\bbi\s*13\b", "b13", q)
    q = re.sub(r"\bbee\s*15\b", "b15", q)
    q = re.sub(r"\bbe\s*15\b", "b15", q)
    q = re.sub(r"\bbi\s*15\b", "b15", q)

   
    # TRANSKRIPTKORREKTUR
    
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
        r"\bwas bedeutete die vierte dimension fur ([^?]+)\b",
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