import re


def normalize_query(text: str) -> str:
    if not text:
        return ""

    q = text.strip().lower()

    q = q.replace("–", "-").replace("—", "-")
    q = q.replace("ě", "e").replace("č", "c").replace("ł", "l")
    q = q.replace("ń", "n").replace("ó", "o").replace("ś", "s").replace("ż", "z").replace("ź", "z")
    q = re.sub(r"\s+", " ", q).strip()
    q = q.rstrip(" .,!?:;")

    q = re.sub(r"^ivan lebte\b", "wann lebte", q)
    q = re.sub(r"^iwan lebte\b", "wann lebte", q)
    q = re.sub(r"^wan lebte\b", "wann lebte", q)
    q = re.sub(r"^wer war\b", "wer ist", q)

    q = re.sub(r"\bim im\b", "im", q)
    q = re.sub(r"\bwassily wassily\b", "wassily", q)

    # Künstlernamen
    q = re.sub(r"\bfango\b", "fangor", q)
    q = re.sub(r"\bfangohr\b", "fangor", q)
    q = re.sub(r"\bvangor\b", "fangor", q)

    q = re.sub(r"\bvojtech\b", "wojciech", q)
    q = re.sub(r"\bvojteh\b", "wojciech", q)
    q = re.sub(r"\bwoitschech\b", "wojciech", q)
    q = re.sub(r"\bwojciek\b", "wojciech", q)
    q = re.sub(r"\bfugner\b", "fangor", q)
    q = re.sub(r"\bfugnor\b", "fangor", q)
    q = re.sub(r"\bf[üu]gner\b", "fangor", q)
    q = re.sub(r"\bvan moor\b", "fangor", q)

    q = re.sub(r"\bviktor\b", "victor", q)

    q = re.sub(r"\bbasarin\b", "vasarely", q)
    q = re.sub(r"\bvasarin\b", "vasarely", q)
    q = re.sub(r"\bbasarely\b", "vasarely", q)
    q = re.sub(r"\bvasarelli\b", "vasarely", q)
    q = re.sub(r"\bvasareli\b", "vasarely", q)
    q = re.sub(r"\bvasaraly\b", "vasarely", q)
    q = re.sub(r"\bvasarili\b", "vasarely", q)
    q = re.sub(r"\bwasarely\b", "vasarely", q)
    q = re.sub(r"\bwasareli\b", "vasarely", q)
    q = re.sub(r"\bwasarili\b", "vasarely", q)
    q = re.sub(r"\bwasaweli\b", "vasarely", q)
    q = re.sub(r"\bwasserew\b", "vasarely", q)
    q = re.sub(r"\bwasserev\b", "vasarely", q)
    q = re.sub(r"\bwassarew\b", "vasarely", q)
    q = re.sub(r"\bwassarev\b", "vasarely", q)
    q = re.sub(r"\bwassereli\b", "vasarely", q)
    q = re.sub(r"\bwassareli\b", "vasarely", q)

    q = re.sub(r"\bbrigitte\b", "bridget", q)
    q = re.sub(r"\bbritta\b", "bridget", q)
    q = re.sub(r"\bbridgit\b", "bridget", q)
    q = re.sub(r"\bbridgett\b", "bridget", q)
    q = re.sub(r"\breil\b", "riley", q)
    q = re.sub(r"\breihl\b", "riley", q)
    q = re.sub(r"\breyl\b", "riley", q)
    q = re.sub(r"\braili\b", "riley", q)
    q = re.sub(r"\breilly\b", "riley", q)
    q = re.sub(r"\breiley\b", "riley", q)
    q = re.sub(r"\bdreiling\b", "riley", q)
    q = re.sub(r"\bdryly\b", "riley", q)
    q = re.sub(r"\bdraily\b", "riley", q)

    q = re.sub(r"\bwassili\b", "wassily", q)
    q = re.sub(r"\bkandinski\b", "kandinsky", q)
    q = re.sub(r"\bkandinskiy\b", "kandinsky", q)
    q = re.sub(r"\bkandisky\b", "kandinsky", q)
    q = re.sub(r"\bbasilikum\b", "kandinsky", q)

    q = re.sub(r"\bmargret\b", "margaret", q)
    q = re.sub(r"\bmargarete\b", "margaret", q)

    q = re.sub(r"\bwenstrub\b", "wenstrup", q)
    q = re.sub(r"\bwenstrüp\b", "wenstrup", q)
    q = re.sub(r"\bbenstrup\b", "wenstrup", q)
    q = re.sub(r"\bwensto\b", "wenstrup", q)
    q = re.sub(r"\bwenstu\b", "wenstrup", q)
    q = re.sub(r"\bwenstru\b", "wenstrup", q)

    # Werke
    q = re.sub(r"\bjabla\b", "yabla", q)
    q = re.sub(r"\bjableh\b", "yabla", q)
    q = re.sub(r"\bjabloh\b", "yabla", q)
    q = re.sub(r"\bjablo\b", "yabla", q)

    q = re.sub(r"\bbukla\b", "boglar", q)
    q = re.sub(r"\bbugla\b", "boglar", q)
    q = re.sub(r"\bbuglar\b", "boglar", q)
    q = re.sub(r"\bbogla\b", "boglar", q)
    q = re.sub(r"\bboklar\b", "boglar", q)
    q = re.sub(r"\bboglarr\b", "boglar", q)
    q = re.sub(r"\bboglár\b", "boglar", q)
    q = re.sub(r"\bbogler\b", "boglar", q)

    q = re.sub(r"\bboglar eins\b", "boglar i", q)
    q = re.sub(r"\bboglar 1\b", "boglar i", q)
    q = re.sub(r"\bboglar one\b", "boglar i", q)
    q = re.sub(r"\bboklar eins\b", "boglar i", q)
    q = re.sub(r"\bboklar 1\b", "boglar i", q)
    q = re.sub(r"\bbukla eins\b", "boglar i", q)
    q = re.sub(r"\bbukla 1\b", "boglar i", q)
    q = re.sub(r"\bbugla eins\b", "boglar i", q)
    q = re.sub(r"\bbugla 1\b", "boglar i", q)
    q = re.sub(r"\bbuglar eins\b", "boglar i", q)
    q = re.sub(r"\bbuglar 1\b", "boglar i", q)

    q = re.sub(r"\bvegaviv zwei\b", "vegaviv ii", q)
    q = re.sub(r"\bvegaviv 2\b", "vegaviv ii", q)

    q = re.sub(r"\bin den schwarzen kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bden schwarzen kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bder schwarze kreis\b", "im schwarzen kreis", q)

    q = re.sub(r"\bclepsydra\b", "klepsydra 1", q)
    q = re.sub(r"\bkleepsydra\b", "klepsydra 1", q)
    q = re.sub(r"\bklepsidra\b", "klepsydra 1", q)
    q = re.sub(r"\bklepsydra eins\b", "klepsydra 1", q)

    q = re.sub(r"\bshili\b", "shih-li", q)
    q = re.sub(r"\bschi li\b", "shih-li", q)
    q = re.sub(r"\bshi li\b", "shih-li", q)

    q = re.sub(r"\bb\s*[\.\-]?\s*13\b", "b13", q)
    q = re.sub(r"\bb\s*[\.\-]?\s*15\b", "b15", q)
    q = re.sub(r"\be\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\be\s*[\.\-]?\s*47\b", "e47", q)

    q = re.sub(r"\bi\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\bi\s*[\.\-]?\s*47\b", "e47", q)

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

    q = re.sub(r"\b4\.64\b", "4-64", q)
    q = re.sub(r"\b4 64\b", "4-64", q)

    # Frageformen
    q = re.sub(r"\berschien\b", "entstand", q)
    q = re.sub(r"\berschienen\b", "entstanden", q)

    q = re.sub(r"^lebte ([a-zäöüß][a-zäöüß\s\-]+)$", r"wann lebte \1", q)
    q = re.sub(r"^wurde ([a-zäöüß][a-zäöüß\s\-]+) geboren$", r"wann wurde \1 geboren", q)
    q = re.sub(r"^sagen wir,?\s*wo die ([a-zäöüß\s\-]+) geboren$", r"wo wurde \1 geboren", q)
    q = re.sub(r"^zu welcher zeit fand das space age statt$", "wann war das space age", q)

    q = re.sub(r"\s+", " ", q).strip()
    return q