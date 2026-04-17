from typing import List, Dict


def format_context(chunks: List[Dict]) -> str:
    if not chunks:
        return "Kein zusätzlicher Kontext verfügbar."

    parts = []
    for i, chunk in enumerate(chunks, start=1):
        source = chunk.get("metadata", {}).get("source", "unknown")
        text = chunk.get("text", "").strip()
        parts.append(f"[Quelle {i}: {source}]\n{text}")

    return "\n\n".join(parts)


def build_system_prompt() -> str:
    return (
        "Du bist ein Museumsassistent. "
        "Beantworte die Frage ausschließlich auf Grundlage des bereitgestellten Kontexts. "
        "Antworte kurz, klar, natürlich und direkt. "
        "Keine Füllwörter, kein Zögern, keine Einleitungen wie 'ähm', 'also' oder 'ich denke'. "
        "Keine Markdown-Formatierung, keine Sternchen, keine Aufzählungen. "
        "Wenn die Information im Kontext enthalten ist, nenne sie direkt. "
        "Wenn sie nur teilweise enthalten ist, sage genau, was im Kontext steht und was nicht. "
        "Wenn bei einer Lebensdaten-Frage nur ein Geburtsdatum, aber kein Sterbedatum im Kontext steht, sage das klar und natürlich. "
        "Wenn bei einer Lebensdaten-Frage sowohl Geburts- als auch Sterbedatum vorhanden sind, nenne beides direkt. "
        "Wenn nach einem Werk gefragt wird und Titel, Jahr oder Künstler im Kontext stehen, nenne diese direkt. "
        "Erfinde keine Fakten und ergänze nichts aus Weltwissen."
    )


def build_user_prompt(query: str, chunks: List[Dict]) -> str:
    context = format_context(chunks)

    return f"""
Frage der Besucherin:
{query}

Verfügbare Kontextinformationen:
{context}

Anweisung:
Beantworte die Frage nur anhand des Kontexts.
Wenn die Antwort im Kontext steht, nenne sie direkt und konkret.
Wenn die Antwort nur teilweise aus dem Kontext hervorgeht, sage genau das.
Bei Fragen nach Lebensdaten:
- Wenn Geburts- und Sterbedatum vorhanden sind, nenne beides.
- Wenn nur das Geburtsdatum vorhanden ist, sage nur das und erwähne, dass kein Sterbedatum im Kontext steht.
- Wenn nur Jahreszahlen vorhanden sind, nenne die Jahreszahlen.
Bei Fragen zu Kunstwerken:
- Nenne möglichst direkt Titel, Künstler und Jahr, sofern sie im Kontext stehen.
Die Ausgabe soll kurz, klar, natürlich und für gesprochene Wiedergabe geeignet sein.
Ohne Markdown, ohne Sternchen, ohne Füllwörter, ohne Zögern.
""".strip()