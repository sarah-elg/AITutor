import gradio as gr
import random
from question_generator import QuestionGenerator
from answer_handler import AnswerHandler
from ui_components import create_tabs
from styles import get_css_styles
from utils import format_choices, get_question_type_code

class GradioInterface:
    def __init__(self, tutor):
        self.tutor = tutor
        self.current_question = {
            "options": {},
            "correct_answers": [],
            "selected_answers": []
        }
        self.question_language = "de"  # Standardsprache für Fragen (Deutsch)
        self.attempt_count = 0  # Zähler für Antwortversuche
        self.max_attempts = 3  # Maximale Anzahl von Versuchen

        # Neue Variablen für Mehrfragen-Funktionalität
        self.question_queue = []  # Queue für generierte Fragen
        self.current_question_index = 0  # Index der aktuellen Frage
        self.total_questions = 0  # Gesamtzahl der Fragen
        self.active_output = "auto"  # Speichert, welches Ausgabefeld aktiv ist

        # Komponenten initialisieren
        self.question_generator = QuestionGenerator(self)
        self.answer_handler = AnswerHandler(self)

    def create_interface(self):
        # Hauptfunktion für das Gradio-Interface
        with gr.Blocks(title="Business Software 2 Tutor") as demo:
            with gr.Row():
                with gr.Column(scale=8):
                    gr.Markdown("## Business Software 2 Tutor")
                with gr.Column(scale=1, min_width=80):
                    gr.Image(value="logo.png", show_label=False)
                    gr.HTML(get_css_styles())

            # Tabs und UI-Komponenten erstellen
            self.components = create_tabs(self)

        return demo

    def set_question_language(self, language):
        self.question_language = "de" if language == "Deutsch" else "en"
        return None

    def ask_question(self, message, history):
        try:
            response = self.tutor.ask_question(message)
            return response
        except Exception as e:
            return f"Fehler bei der Verarbeitung der Frage: {str(e)}"

    def generate_questions(self, question_type, count, topic=None):
        """Generiert mehrere Fragen und speichert sie in der Queue

        Args:
            question_type: Art der Frage (MC oder SC)
            count: Anzahl der zu generierenden Fragen
            topic: Optional - wenn angegeben, werden Fragen zu diesem Thema generiert
        """
        self.question_queue = []
        self.current_question_index = 0
        self.total_questions = int(count)
        self.attempt_count = 0

        # Setze den aktiven Ausgabebereich basierend darauf, ob ein Thema angegeben wurde
        self.active_output = "eigene" if topic else "auto"

        # Generiere die angegebene Anzahl von Fragen
        successful_questions = 0
        max_attempts = self.total_questions * 2
        attempts = 0

        while successful_questions < self.total_questions and attempts < max_attempts:
            attempts += 1
            try:
                # Unterschiedliche Fragengenerierung basierend auf dem Modus
                if topic:
                    # Eigene Fragen zu einem bestimmten Thema
                    if not topic.strip():
                        error_msg = "Bitte geben Sie ein Thema ein" if self.question_language == "de" else "Please enter a topic"
                        return error_msg, gr.update(visible=False), gr.update(choices=[]), "", 0, gr.update(visible=False), gr.update(visible=False)

                    q_type_code = get_question_type_code(question_type)

                    # Entscheide, ob es die erste Frage ist oder eine Variation
                    if successful_questions > 0:
                        try:
                            # Hole relevante Dokumente aus dem Vektorspeicher
                            docs = self.tutor.vectorstore.similarity_search(
                                topic,
                                k=2,
                                filter={"source_type": "Hauptskript"}
                            )

                            # Extrahiere den Kontext aus den Dokumenten
                            if docs:
                                context = docs[0].page_content
                            else:
                                context = "Keine spezifischen Informationen verfügbar."

                            # Neuer Prompt mit Kontext-Einbindung
                            variation_prompt = f"""
                            Du bist ein Experte für Business Software und Prüfungsvorbereitung.
                            Generiere eine SPEZIFISCHE Prüfungsfrage zum Thema '{topic}', die sich von bisherigen Fragen deutlich unterscheidet.

                            Basiere deine Frage auf folgendem Kontext aus dem Kursmaterial:
                            '{context}'

                            Wichtig: Fokussiere auf einen ANDEREN Aspekt oder Teilbereich des Themas als zuvor.
                            Wähle einen der folgenden Ansätze:
                            - Praktische Anwendung statt Theorie
                            - Spezifische Technologie oder Methode
                            - Vor- oder Nachteile
                            - Implementierungsherausforderungen
                            - Historische Entwicklung
                            - Vergleich mit alternativen Konzepten
                            - Zukunftsperspektiven

                            Formuliere eine präzise, prüfungsrelevante Frage ohne Einleitung oder Erklärung.
                            """

                            # Verwende den formatierten Prompt
                            subtopic = self.tutor.llm.invoke(variation_prompt).strip()

                            # Entferne Anführungszeichen und andere Formatierungen
                            subtopic = subtopic.replace('"', '').replace("'", "").strip()
                            # Kombiniere Hauptthema und Unterthema
                            current_topic = f"{topic} - {subtopic}"
                        except Exception as e:
                            print(f"Fehler bei der Unterthema-Generierung: {e}")
                            # Fallback: Füge eine einfache Variation hinzu
                            current_topic = f"{topic} (Variation {successful_questions + 1})"
                    else:
                        current_topic = topic

                    print(f"Generiere Frage zu: {current_topic}")
                    question_data = self.question_generator.generate_question_with_language(current_topic, q_type_code)

                    if "error" not in question_data and "options" in question_data and question_data["options"] and len(question_data["options"]) >= 2:
                        # Füge Fragetyp hinzu
                        question_data["question_type"] = question_type
                        self.question_queue.append(question_data)
                        successful_questions += 1
                else:
                    # Automatische Fragen mit zufälligen Themen
                    question_data = self.question_generator.generate_random_question_internal(question_type)
                    if "options" in question_data and question_data["options"] and len(question_data["options"]) >= 2:
                        self.question_queue.append(question_data)
                        successful_questions += 1
            except Exception as e:
                print(f"Fehler bei der Fragengenerierung: {e}")
                continue

        # Aktualisiere die tatsächliche Anzahl der Fragen
        self.total_questions = len(self.question_queue)

        # Zeige die erste Frage an
        if self.question_queue:
            # Bestimme, welches Ausgabefeld aktualisiert werden soll
            question_data = self.question_queue[0]

            # Setze die aktuelle Frage
            self.current_question["options"] = question_data["options"]
            self.current_question["correct_answers"] = self.tutor.last_correct_answers
            q_type = get_question_type_code(question_data.get("question_type", "Multiple Choice (MC)"))
            self.current_question["question_type"] = q_type

            # Fortschrittsanzeige
            progress = f"Frage 1 von {self.total_questions}" if self.question_language == "de" else f"Question 1 of {self.total_questions}"
            question_text = f"{progress}\n\n{question_data['question_text']}"

            choices = format_choices(question_data["options"])

            if self.active_output == "auto":
                return question_text, gr.update(visible=True), gr.update(choices=choices, value=[]), "", 0, gr.update(visible=True, value=progress), gr.update(visible=False)
            else:
                return question_text, gr.update(visible=True), gr.update(choices=choices, value=[]), "", 0, gr.update(visible=True, value=progress), gr.update(visible=False)
        else:
            error_msg = "Fehler bei der Fragengenerierung" if self.question_language == "de" else "Error generating questions"
            return error_msg, gr.update(visible=False), gr.update(choices=[]), "", 0, gr.update(visible=False), gr.update(visible=False)