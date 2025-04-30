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