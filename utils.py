def format_choices(options):
    """Formatiert Antwortoptionen für die Anzeige"""
    return [f"{k}) {v}" for k, v in options.items()]

def get_question_type_code(question_type):
    """Konvertiert den Fragetyp in einen Code"""
    return "mc" if "Multiple" in question_type else "sc"

def format_progress_text(current, total, language="de"):
    """Formatiert den Fortschrittstext"""
    if language == "de":
        return f"Frage {current} von {total}"
    else:
        return f"Question {current} of {total}"

def get_end_message(language="de"):
    """Liefert die Nachricht am Ende aller Fragen"""
    if language == "de":
        return "Alle Fragen beantwortet! Generieren Sie neue Fragen."
    else:
        return "All questions answered! Generate new questions."

def error_handler(e, language="de"):
    """Behandelt Fehler bei der Verarbeitung"""
    if language == "de":
        return f"Fehler: {str(e)}"
    else:
        return f"Error: {str(e)}"

def get_relevant_documents(vectorstore, query, k=2, filter_type=None):
    """Zentrale Funktion zum Abrufen relevanter Dokumente"""
    filter_dict = {"source_type": filter_type} if filter_type else None
    try:
        docs = vectorstore.similarity_search(
            query,
            k=k,
            filter=filter_dict
        )
        return docs
    except Exception as e:
        print(f"Fehler beim Abrufen von Dokumenten: {e}")
        return []

def extract_key_topic(text, llm):
    """Extrahiert ein Schlüsselthema aus dem Text ohne Vorgaben"""
    prompt = f"""
    Du bist ein Experte für Business Software 2.
    Extrahiere ein einzelnes, präzises Fachthema aus dem folgenden Text, das sich für eine Prüfungsfrage eignet.
    Das Thema sollte spezifisch genug sein, um eine fokussierte Frage zu ermöglichen.
    Gib nur das Thema zurück, ohne zusätzlichen Text oder Erklärungen.

    Text: {text[:800]}
    """

    try:
        topic = llm.invoke(prompt).strip()
        topic = topic.replace('"', '').replace("'", "").strip()
        if len(topic) > 50:
            topic = topic[:50]
        return topic
    except Exception as e:
        print(f"Fehler bei der Themenextraktion: {e}")
        return "Business Software"