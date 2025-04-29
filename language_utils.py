def detect_language(text):
    """
    Erkennt die Sprache des Textes (Deutsch oder Englisch)
    Returns: 'de' für Deutsch, 'en' für Englisch
    """
    # Liste deutscher Wörter und Zeichen für die Erkennung
    german_indicators = [
        'der', 'die', 'das', 'und', 'ist', 'in', 'zu', 'den', 'für', 'auf', 'mit', 'sich',
        'des', 'ein', 'eine', 'einen', 'dem', 'nicht', 'von', 'es', 'ich', 'du', 'wir',
        'sie', 'ihr', 'mir', 'mich', 'dir', 'dich', 'was', 'wie', 'wer', 'wo', 'warum',
        'wieso', 'weshalb', 'welche', 'welcher', 'welches', 'kann', 'könnte', 'würde',
        'möchte', 'bitte', 'danke', 'hallo', 'tschüss', 'auf', 'unter', 'über', 'neben',
        'zwischen', 'vor', 'nach', 'bei', 'seit', 'während', 'wegen', 'trotz', 'durch',
        'gegen', 'ohne', 'um', 'herum', 'entlang', 'bis', 'ab', 'aus', 'außer', 'bei',
        'gegenüber', 'gemäß', 'laut', 'zufolge', 'entsprechend', 'statt', 'anstatt',
        'anstelle', 'außerhalb', 'innerhalb', 'oberhalb', 'unterhalb', 'diesseits',
        'jenseits', 'beiderseits', 'abseits', 'unweit', 'ä', 'ö', 'ü', 'ß'
    ]

    # Normalisiere den Text für den Vergleich
    text_lower = text.lower()
    words = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text_lower).split()

    # Zähle deutsche Indikatoren
    german_count = sum(1 for word in words if word in german_indicators)
    german_chars_count = sum(1 for c in text_lower if c in 'äöüß')

    # Heuristik: Wenn mehr als 2 deutsche Indikatoren oder deutsche Sonderzeichen gefunden wurden,
    # oder wenn bestimmte deutsche Wörter vorkommen, ist es wahrscheinlich Deutsch
    if german_count > 2 or german_chars_count > 0 or any(word in text_lower for word in ['wie', 'was', 'warum', 'wieso', 'weshalb', 'welche']):
        return 'de'
    else:
        return 'en'

def get_prompt_by_language(language, question, documents):
    """
    Erstellt einen Prompt basierend auf der erkannten Sprache
    """
    if language == 'de':
        prompt = f"""
        Du bist ein hilfreicher BS2-Tutor für das Fach "Business Software 2".
        Beantworte die folgende Frage basierend auf den gegebenen Informationen.
        Verwende nur die bereitgestellten Informationen. Wenn du die Antwort nicht in den
        Informationen findest, sage das ehrlich.
        Antworte auf Deutsch.

        Frage: {question}

        Relevante Informationen:
        """
    else:  # 'en'
        prompt = f"""
        You are a helpful BS2 tutor for the subject "Business Software 2".
        Answer the following question based on the provided information.
        Use only the information provided. If you cannot find the answer in the
        information, say so honestly.
        Answer in English.

        Question: {question}

        Relevant information:
        """

    for i, doc in enumerate(documents):
        source_type = doc.metadata.get('source_type', 'Unknown' if language == 'en' else 'Unbekannt')
        file_name = doc.metadata.get('file_name', 'Unknown' if language == 'en' else 'Unbekannt')
        page = doc.metadata.get('page', 'Unknown' if language == 'en' else 'Unbekannt')

        if language == 'de':
            prompt += f"\n[{i+1}] Quelle: {source_type} ({file_name}, Seite {page+1})\n"
        else:  # 'en'
            prompt += f"\n[{i+1}] Source: {source_type} ({file_name}, Page {page+1})\n"

        prompt += f"{doc.page_content}\n"

    return prompt

def format_response_by_language(language, answer, documents, source_label):
    """
    Formatiert die Antwort mit Quellenangaben basierend auf der erkannten Sprache
    """
    if language == 'de':
        response = f"\nAntwort: {answer}\n\nQuellen ({source_label}):"
    else:  # 'en'
        response = f"\nAnswer: {answer}\n\nSources ({source_label}):"

    for i, doc in enumerate(documents):
        source_type = doc.metadata.get('source_type', 'Unknown' if language == 'en' else 'Unbekannt')
        file_name = doc.metadata.get('file_name', 'Unknown' if language == 'en' else 'Unbekannt')
        page = doc.metadata.get('page', 'Unknown' if language == 'en' else 'Unbekannt')

        if language == 'de':
            response += f"\n[{i+1}] {source_type}: {file_name}, Seite {page + 1}"
        else:  # 'en'
            response += f"\n[{i+1}] {source_type}: {file_name}, Page {page + 1}"

    return response

def is_insufficient_answer(answer, language='de'):
    """Prüft, ob eine Antwort unzureichend ist"""
    if language == 'de':
        insufficient_phrases = [
            "keine ausreichenden informationen",
            "nicht genügend informationen",
            "keine informationen",
            "nicht genug kontext",
            "kann ich nicht beantworten",
            "nicht in den bereitgestellten informationen"
        ]
    else:  # 'en'
        insufficient_phrases = [
            "no sufficient information",
            "not enough information",
            "no information",
            "not enough context",
            "cannot answer",
            "not in the provided information"
        ]

    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in insufficient_phrases)