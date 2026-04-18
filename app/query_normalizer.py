import re


def normalize_query(text: str) -> str:
    if not text:
        return text

    q = text.strip().lower()

    # Grundbereinigung
    q = q.replace("–", "-").replace("—", "-")
    q = re.sub(r"\s+", " ", q)

    # Häufige STT-Artefakte
    q = re.sub(r"\bim im\b", "im", q)
    q = re.sub(r"\bwassily wassily\b", "wassily", q)

    # Frageanfänge glätten
    q = re.sub(r"\bvan\b", "wann", q)
    q = re.sub(r"\bwan\b", "wann", q)

    # ---------------------------------
    # Frageformulierungen vereinheitlichen
    # ---------------------------------
    q = re.sub(r"\berschienen\b", "entstanden", q)
    q = re.sub(r"\berschien\b", "entstand", q)

    q = re.sub(r"\bwann ist (.+?) erschienen\b", r"wann entstand \1", q)
    q = re.sub(r"\bwann erschien (.+?)\b", r"wann entstand \1", q)

    # ---------------------------------
    # Künstlernamen / bekannte Varianten
    # ---------------------------------
    q = re.sub(r"\bfango\b", "fangor", q)
    q = re.sub(r"\bvojtech\b", "wojciech", q)
    q = re.sub(r"\bvojte[ch]?\b", "wojciech", q)

    q = re.sub(r"\bvasarelli\b", "vasarely", q)
    q = re.sub(r"\bbasarili\b", "vasarely", q)
    q = re.sub(r"\bvasarili\b", "vasarely", q)
    q = re.sub(r"\bviktor vasarely\b", "victor vasarely", q)

    q = re.sub(r"\bmargret\b", "margaret", q)
    q = re.sub(r"\bwenstrub\b", "wenstrup", q)
    q = re.sub(r"\bwenstrüp\b", "wenstrup", q)
    q = re.sub(r"\bbenstrup\b", "wenstrup", q)

    q = re.sub(r"\bbritta reilly\b", "bridget riley", q)
    q = re.sub(r"\bbritta riley\b", "bridget riley", q)
    q = re.sub(r"\bbridgit riley\b", "bridget riley", q)
    q = re.sub(r"\bbridgit reilly\b", "bridget riley", q)
    q = re.sub(r"\breilly\b", "riley", q)

    # ---------------------------------
    # Werktitel / problematische STT-Fälle
    # ---------------------------------

    # Yabla
    q = re.sub(r"\bjabla\b", "yabla", q)
    q = re.sub(r"\bjableh\b", "yabla", q)
    q = re.sub(r"\bjabloh\b", "yabla", q)
    q = re.sub(r"\bjablo\b", "yabla", q)
    q = re.sub(r"\byable\b", "yabla", q)
    q = re.sub(r"\byableh\b", "yabla", q)

    # Boglar I / häufige STT-Fehler
    q = re.sub(r"\bbukla\b", "boglar", q)
    q = re.sub(r"\bbogla\b", "boglar", q)
    q = re.sub(r"\bboklar\b", "boglar", q)
    q = re.sub(r"\bboglár\b", "boglar", q)
    q = re.sub(r"\bbogler\b", "boglar", q)

    q = re.sub(r"\bboglar eins\b", "boglar i", q)
    q = re.sub(r"\bboglar 1\b", "boglar i", q)
    q = re.sub(r"\bboklar eins\b", "boglar i", q)
    q = re.sub(r"\bboklar 1\b", "boglar i", q)
    q = re.sub(r"\bbukla eins\b", "boglar i", q)
    q = re.sub(r"\bbukla 1\b", "boglar i", q)
    q = re.sub(r"\bboglar one\b", "boglar i", q)
    q = re.sub(r"\bboklar one\b", "boglar i", q)

    # Im schwarzen Kreis
    q = re.sub(r"\bin den schwarzen kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bder schwarze kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bin schwarzen kreis\b", "im schwarzen kreis", q)

    # Farbbewegung
    q = re.sub(r"\b4\.64\b", "4-64", q)
    q = re.sub(r"\b4 64\b", "4-64", q)

    # Weitere Werktitel
    q = re.sub(r"\bshih li\b", "shih-li", q)
    q = re.sub(r"\bshihli\b", "shih-li", q)
    q = re.sub(r"\bklepsydra eins\b", "klepsydra 1", q)
    q = re.sub(r"\bklepsydra one\b", "klepsydra 1", q)

    # ---------------------------------
    # Fangor-Codes robust machen
    # ---------------------------------
    q = re.sub(r"\bbeat\s*\.?\s*13\b", "b13", q)
    q = re.sub(r"\bbeat\s*\.?\s*15\b", "b15", q)

    q = re.sub(r"\bbild\s*\.?\s*13\b", "b13", q)
    q = re.sub(r"\bbild\s*\.?\s*15\b", "b15", q)

    q = re.sub(r"\bb\s*[\.\-]?\s*13\b", "b13", q)
    q = re.sub(r"\bb\s*[\.\-]?\s*15\b", "b15", q)

    q = re.sub(r"\be\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\be\s*[\.\-]?\s*47\b", "e47", q)

    q = re.sub(r"\bbee\s*13\b", "b13", q)
    q = re.sub(r"\bbe\s*13\b", "b13", q)
    q = re.sub(r"\bbi\s*13\b", "b13", q)

    q = re.sub(r"\bbee\s*15\b", "b15", q)
    q = re.sub(r"\bbe\s*15\b", "b15", q)
    q = re.sub(r"\bbi\s*15\b", "b15", q)

    # ---------------------------------
    # Aufräumen
    # ---------------------------------
    q = re.sub(r"\s+", " ", q).strip()

    return q