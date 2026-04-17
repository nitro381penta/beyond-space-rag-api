import re


def normalize_query(text: str) -> str:
    if not text:
        return text

    q = text.strip().lower()

    # Sonderzeichen / Bindestrich-Varianten glätten
    q = q.replace("–", "-").replace("—", "-")
    q = re.sub(r"\s+", " ", q)

    # Häufige Dopplungen / STT-Artefakte
    q = re.sub(r"\bim im\b", "im", q)
    q = re.sub(r"\bwassily wassily\b", "wassily", q)

    # ---------------------------------
    # Künstlernamen / bekannte Varianten
    # ---------------------------------
    q = re.sub(r"\bfango\b", "fangor", q)
    q = re.sub(r"\bvojtech\b", "wojciech", q)
    q = re.sub(r"\bvojte[ch]?\b", "wojciech", q)

    q = re.sub(r"\bvasarelli\b", "vasarely", q)
    q = re.sub(r"\bviktor vasarely\b", "victor vasarely", q)

    q = re.sub(r"\bmargret\b", "margaret", q)
    q = re.sub(r"\bwenstrub\b", "wenstrup", q)
    q = re.sub(r"\bwenstrüp\b", "wenstrup", q)
    q = re.sub(r"\bbenstrup\b", "wenstrup", q)

    # ---------------------------------
    # Werktitel / problematische STT-Fälle
    # ---------------------------------

    # Yabla
    q = re.sub(r"\bjabla\b", "yabla", q)
    q = re.sub(r"\bjableh\b", "yabla", q)
    q = re.sub(r"\bjabloh\b", "yabla", q)
    q = re.sub(r"\bjablo\b", "yabla", q)

    # Boglar I
    q = re.sub(r"\bbukla\b", "boglar", q)
    q = re.sub(r"\bbogla\b", "boglar", q)
    q = re.sub(r"\bboglár\b", "boglar", q)
    q = re.sub(r"\bboglar eins\b", "boglar i", q)
    q = re.sub(r"\bboglar 1\b", "boglar i", q)
    q = re.sub(r"\bbukla eins\b", "boglar i", q)
    q = re.sub(r"\bbukla 1\b", "boglar i", q)

    # Im schwarzen Kreis
    q = re.sub(r"\bin den schwarzen kreis\b", "im schwarzen kreis", q)

    # Farbbewegung
    q = re.sub(r"\b4\.64\b", "4-64", q)
    q = re.sub(r"\b4 64\b", "4-64", q)

    # ---------------------------------
    # Fangor-Codes robust machen
    # ---------------------------------

    # "beat 13" -> "b13"
    q = re.sub(r"\bbeat\s*\.?\s*13\b", "b13", q)
    q = re.sub(r"\bbeat\s*\.?\s*15\b", "b15", q)

    # "bild 13" -> "b13"
    q = re.sub(r"\bbild\s*\.?\s*13\b", "b13", q)
    q = re.sub(r"\bbild\s*\.?\s*15\b", "b15", q)

    # "b. 13" -> "b13"
    q = re.sub(r"\bb\s*[\.\-]?\s*13\b", "b13", q)
    q = re.sub(r"\bb\s*[\.\-]?\s*15\b", "b15", q)

    # "e. 37" -> "e37"
    q = re.sub(r"\be\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\be\s*[\.\-]?\s*47\b", "e47", q)

    # Optional: "bee 13" / "bi 13" / "be 13" abfangen
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