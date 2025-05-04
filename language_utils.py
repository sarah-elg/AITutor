def detect_language(text):
    """
    Erkennt die Sprache des Textes (Deutsch oder Englisch)
    Returns: 'de' für Deutsch, 'en' für Englisch
    """
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

    text_lower = text.lower()
    words = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text_lower).split()

    german_count = sum(1 for word in words if word in german_indicators)
    german_chars_count = sum(1 for c in text_lower if c in 'äöüß')

    if german_count > 2 or german_chars_count > 0 or any(word in text_lower for word in ['wie', 'was', 'warum', 'wieso', 'weshalb', 'welche']):
        return 'de'
    else:
        return 'en'

def format_response_by_language(language, answer, documents, source_label):
    """
    Formatiert die Antwort mit Quellenangaben basierend auf der erkannten Sprache
    """
    if language == 'de':
        response = f"\nAntwort: {answer}\n\nQuellen ({source_label}):"
    else: 
        response = f"\nAnswer: {answer}\n\nSources ({source_label}):"

    for i, doc in enumerate(documents):
        source_type = doc.metadata.get('source_type', 'Unknown' if language == 'en' else 'Unbekannt')
        file_name = doc.metadata.get('file_name', 'Unknown' if language == 'en' else 'Unbekannt')
        page = doc.metadata.get('page', 'Unknown' if language == 'en' else 'Unbekannt')

        if language == 'de':
            response += f"\n[{i+1}] {source_type}: {file_name}, Seite {page + 1}"
        else:  
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
    else:  
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

def get_error_message(language, error_type):
    """Liefert Fehlermeldungen in der angegebenen Sprache"""
    error_messages = {
        "no_documents": {
            "de": "Keine relevanten Dokumente gefunden",
            "en": "No relevant documents found"
        },
        "question_generation": {
            "de": "Fehler bei der Fragengenerierung",
            "en": "Error generating question"
        },
        "invalid_question": {
            "de": "Konnte keine gültige Frage generieren",
            "en": "Could not generate a valid question"
        },
        "json_parse": {
            "de": "Konnte das JSON-Format nicht korrekt parsen",
            "en": "Could not parse the JSON format correctly"
        },
        "no_vectorstore_docs": {
            "de": "Keine Dokumente im Vektorspeicher gefunden",
            "en": "No documents found in vector store"
        },
        "empty_topic": {
            "de": "Bitte geben Sie ein Thema ein",
            "en": "Please enter a topic"
        }
    }

    return error_messages.get(error_type, {}).get(language, "Unknown error")