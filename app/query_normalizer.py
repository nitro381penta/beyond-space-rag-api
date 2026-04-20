import re
import unicodedata


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )


def normalize_query(text: str) -> str:
    if not text:
        return ""

    q = text.strip().lower()

    # Unicode / Sonderzeichen vereinheitlichen
    q = q.replace("–", "-").replace("—", "-")
    q = q.replace("’", "'").replace("`", "'")
    q = _strip_accents(q)

    # deutsche Umlaute robust vereinheitlichen
    q = q.replace("ß", "ss")

    # Leerzeichen bereinigen
    q = re.sub(r"\s+", " ", q).strip()

    # Satzzeichen am Ende entfernen
    q = re.sub(r"[?!.,;:]+$", "", q)

   
    # Allgemeine STT-Artefakte / Frageformen
    
    q = re.sub(r"\bim im\b", "im", q)
    q = re.sub(r"\bwassily wassily\b", "wassily", q)

    # Frageanfänge glätten
    q = re.sub(r"^schien\b", "wann entstand", q)
    q = re.sub(r"^erschien\b", "wann entstand", q)
    q = re.sub(r"^erschienen\b", "wann entstanden", q)

    # typische Fehlformen bei Frageanfängen
    q = re.sub(r"\bwer war\b", "wer ist", q)
    q = re.sub(r"\bwer hat\b", "wer malte", q)

    # falls STT „erschien“ statt „entstand“ liefert
    q = re.sub(r"\berschien\b", "entstand", q)
    q = re.sub(r"\berschienen\b", "entstanden", q)

   
    # KÜNSTLERNAMEN

    # Fangor / Wojciech
    q = re.sub(r"\bfango\b", "fangor", q)
    q = re.sub(r"\bfangor\b", "fangor", q)
    q = re.sub(r"\bvojtech\b", "wojciech", q)
    q = re.sub(r"\bvojteh\b", "wojciech", q)
    q = re.sub(r"\bvojtec\b", "wojciech", q)
    q = re.sub(r"\bvojt[e]?ch\b", "wojciech", q)
    q = re.sub(r"\bwoitschech\b", "wojciech", q)

    # Vasarely / Victor
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
    q = re.sub(r"\bwasarelli\b", "vasarely", q)

    # Bridget Riley
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
    q = re.sub(r"\bbridget dryley\b", "bridget riley", q)
    q = re.sub(r"\bbritta riley\b", "bridget riley", q)
    q = re.sub(r"\bbritta reil\b", "bridget riley", q)
    q = re.sub(r"\bbritta dreiling\b", "bridget riley", q)

    # sehr typische Fehltranskripte
    q = re.sub(r"\bwir haben abgetrocknet\b", "wer ist bridget riley", q)
    q = re.sub(r"\bich bin liebti britta dreiling\b", "wann lebte bridget riley", q)
    q = re.sub(r"\bcant leave the bridge dryly\b", "wer ist bridget riley", q)
    q = re.sub(r"\bcan't leave the bridge dryly\b", "wer ist bridget riley", q)

    # Wenstrup
    q = re.sub(r"\bmargret\b", "margaret", q)
    q = re.sub(r"\bwenstrub\b", "wenstrup", q)
    q = re.sub(r"\bwenstrup\b", "wenstrup", q)
    q = re.sub(r"\bwenstrupf\b", "wenstrup", q)
    q = re.sub(r"\bwenstrupp\b", "wenstrup", q)
    q = re.sub(r"\bwenstrups\b", "wenstrup", q)
    q = re.sub(r"\bwenstrup kreisel\b", "kreisel von margaret wenstrup", q)

    # Kandinsky
    q = re.sub(r"\bkandinski\b", "kandinsky", q)
    q = re.sub(r"\bkandisky\b", "kandinsky", q)
    q = re.sub(r"\bwassili\b", "wassily", q)
    q = re.sub(r"\bwasili\b", "wassily", q)

    # Andrade / Stanczak
    q = re.sub(r"\bandreid\b", "andrade", q)
    q = re.sub(r"\bandradee\b", "andrade", q)
    q = re.sub(r"\bstancak\b", "stanczak", q)
    q = re.sub(r"\bstancsack\b", "stanczak", q)
    q = re.sub(r"\bstanzak\b", "stanczak", q)

    
    # WERKTITEL

    # Yabla
    q = re.sub(r"\bjabla\b", "yabla", q)
    q = re.sub(r"\bjableh\b", "yabla", q)
    q = re.sub(r"\bjabloh\b", "yabla", q)
    q = re.sub(r"\bjablo\b", "yabla", q)

    # Boglar I
    q = re.sub(r"\bbukla\b", "boglar", q)
    q = re.sub(r"\bbugla\b", "boglar", q)
    q = re.sub(r"\bbuglar\b", "boglar", q)
    q = re.sub(r"\bbogla\b", "boglar", q)
    q = re.sub(r"\bboklar\b", "boglar", q)
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

    # Im schwarzen Kreis
    q = re.sub(r"\bin den schwarzen kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bden schwarzen kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bder schwarze kreis\b", "im schwarzen kreis", q)
    q = re.sub(r"\bdas werk im schwarzen kreis\b", "im schwarzen kreis", q)

    # Klepsydra
    q = re.sub(r"\bclepsydra\b", "klepsydra", q)
    q = re.sub(r"\bkleepsydra\b", "klepsydra", q)
    q = re.sub(r"\bklepsidra\b", "klepsydra", q)
    q = re.sub(r"\bklepsydra eins\b", "klepsydra 1", q)

    # Shih-Li
    q = re.sub(r"\bshili\b", "shih-li", q)
    q = re.sub(r"\bschi li\b", "shih-li", q)
    q = re.sub(r"\bshi li\b", "shih-li", q)

    # Codes B/E-Werke
    q = re.sub(r"\bb\s*[\.\-]?\s*13\b", "b13", q)
    q = re.sub(r"\bb\s*[\.\-]?\s*15\b", "b15", q)
    q = re.sub(r"\be\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\be\s*[\.\-]?\s*47\b", "e47", q)

    # STT verwechselt E oft mit I
    q = re.sub(r"\bi\s*[\.\-]?\s*37\b", "e37", q)
    q = re.sub(r"\bi\s*[\.\-]?\s*47\b", "e47", q)

    
    # Frageintention glätten

    # Künstlerfrage zum Werk
    q = re.sub(
        r"\bwer malte das werk ([a-z0-9äöüss\-\']+)\b",
        r"von wem ist das werk \1",
        q
    )

    q = re.sub(
        r"\bwer hat das werk ([a-z0-9äöüss\-\']+) gemalt\b",
        r"von wem ist das werk \1",
        q
    )

    q = re.sub(
        r"\bwer hat das ([a-z0-9äöüss\-\']+) gemalt\b",
        r"von wem ist \1",
        q
    )

    # "wann wurde X geboren" etc.
    q = re.sub(r"\bwer war ([a-z][a-z\s\-]+)\b", r"wer ist \1", q)

    # häufiger Fall bei Wenstrup/Kreisel
    q = re.sub(
        r"\bwer hat das wenstrup kreisel gemalt\b",
        "von wem ist kreisel von margaret wenstrup",
        q
    )

    # Leerzeichen final bereinigen
    q = re.sub(r"\s+", " ", q).strip()
    return q