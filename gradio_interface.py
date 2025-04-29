import gradio as gr
import random

class GradioInterface:
    def __init__(self, tutor):
        self.tutor = tutor
        self.current_question = {
            "options": {},
            "correct_answers": [],
            "selected_answers": []
        }
        self.question_language = "de"  # Standardsprache für Fragen (Deutsch)

    def create_interface(self):
        # Hauptfunktion für das Gradio-Interface
        with gr.Blocks(title="BS2 Tutor") as demo:
            gr.Markdown("# BS2 Tutor")

            with gr.Tabs() as tabs:
                # Tab 1: Fragen-Modus
                with gr.TabItem("Fragen"):
                    gr.Markdown("Stellen Sie Ihre Fragen zum BS2-Stoff")
                    fragen_chat = gr.ChatInterface(
                        self.ask_question,
                        examples=["Was ist Process Mining?", "Erkläre OLAP", "Was ist ein Data Warehouse?", 
                                 "What is Process Mining?", "Explain OLAP", "What is a Data Warehouse?"],
                        title="BS2 Fragen"
                    )

                # Tab 2: Trainer
                with gr.TabItem("Trainer"):
                    # Umschalter-Buttons für Fragetypen
                    with gr.Row(equal_height=True):
                        auto_btn = gr.Button("Automatische Fragen", size="lg", variant="primary")
                        eigene_btn = gr.Button("Eigene Fragen", size="lg")

                    # Sprachauswahl für Fragen
                    with gr.Row():
                        question_language = gr.Radio(
                            ["Deutsch", "English"],
                            value="Deutsch",
                            label="Sprache für Fragen / Language for questions"
                        )

                    # Automatische Fragen-Bereich
                    with gr.Column(visible=True) as auto_fragen_bereich:
                        gr.Markdown("### Automatische Fragen")
                        gr.Markdown("Lassen Sie sich automatisch Fragen generieren")

                        # Fragetyp für automatische Fragen
                        auto_question_type = gr.Radio(
                            ["Multiple Choice (MC)", "Single Choice (SC)"],
                            value="Multiple Choice (MC)",
                            label="Fragetyp"
                        )

                        auto_question_btn = gr.Button("Neue Frage")
                        auto_question_output = gr.Markdown("Klicken Sie auf 'Neue Frage', um eine Frage zu generieren")

                    # Eigene Fragen-Bereich
                    with gr.Column(visible=False) as eigene_fragen_bereich:
                        gr.Markdown("### Eigene Fragen")
                        gr.Markdown("Erstellen Sie eigene Fragen zu einem bestimmten Thema")

                        # Eingabefeld für das Thema
                        eigene_topic = gr.Textbox(
                            placeholder="Geben Sie ein Thema ein (z.B. 'Process Mining')",
                            label="Thema"
                        )

                        # Fragetyp für eigene Fragen
                        eigene_type = gr.Radio(
                            ["Multiple Choice (MC)", "Single Choice (SC)"],
                            value="Multiple Choice (MC)",
                            label="Fragetyp"
                        )

                        eigene_question_btn = gr.Button("Frage erstellen")
                        eigene_question_output = gr.Markdown("Hier erscheint Ihre Frage")

                    # Gemeinsame Antwortbuttons-Gruppe (wird für beide Fragetypen verwendet)
                    with gr.Group(visible=False) as buttons_group:
                        gr.Markdown("### Wähle die richtige(n) Antwort(en):")

                        # Jeder Button in einer eigenen Zeile
                        btn_a = gr.Button("A", scale=1)
                        btn_b = gr.Button("B", scale=1)
                        btn_c = gr.Button("C", scale=1)
                        btn_d = gr.Button("D", scale=1)

                        # Ausgewählte Antworten anzeigen
                        selected = gr.Markdown("Ausgewählte Antworten: ")

                        # Button zum Überprüfen der Antwort
                        check_btn = gr.Button("Antwort prüfen", visible=False)
                        result = gr.Markdown("")

                    # Umschaltfunktionen für die Buttons
                    def show_auto_fragen():
                        return gr.update(visible=True), gr.update(visible=False), gr.update(variant="primary"), gr.update(variant="secondary")

                    def show_eigene_fragen():
                        return gr.update(visible=False), gr.update(visible=True), gr.update(variant="secondary"), gr.update(variant="primary")

                    # Event-Handler für die Umschaltbuttons
                    auto_btn.click(
                        show_auto_fragen,
                        outputs=[auto_fragen_bereich, eigene_fragen_bereich, auto_btn, eigene_btn]
                    )

                    eigene_btn.click(
                        show_eigene_fragen,
                        outputs=[auto_fragen_bereich, eigene_fragen_bereich, auto_btn, eigene_btn]
                    )

                    # Event-Handler für Sprachauswahl
                    question_language.change(
                        self.set_question_language,
                        inputs=[question_language]
                    )

                    # Event-Handler für automatische Fragen
                    auto_question_btn.click(
                        self.generate_random_question,
                        inputs=[auto_question_type],
                        outputs=[auto_question_output, eigene_question_output, buttons_group, check_btn, selected]
                    )

                    # Event-Handler für eigene Fragen
                    eigene_question_btn.click(
                        self.create_question,
                        inputs=[eigene_topic, eigene_type],
                        outputs=[eigene_question_output, auto_question_output, buttons_group, check_btn, selected]
                    )

                    # Handler für die Antwortbuttons
                    btn_a.click(lambda s: self.toggle_answer("A", s), inputs=[selected], outputs=[selected])
                    btn_b.click(lambda s: self.toggle_answer("B", s), inputs=[selected], outputs=[selected])
                    btn_c.click(lambda s: self.toggle_answer("C", s), inputs=[selected], outputs=[selected])
                    btn_d.click(lambda s: self.toggle_answer("D", s), inputs=[selected], outputs=[selected])

                    # Handler für den Prüfen-Button
                    check_btn.click(self.check_answer, outputs=[result])

            return demo

    def set_question_language(self, language):
        """Setzt die Sprache für die Fragen"""
        self.question_language = "de" if language == "Deutsch" else "en"
        return None

    def ask_question(self, message, history):
        try:
            response = self.tutor.ask_question(message)
            return response
        except Exception as e:
            return f"Fehler bei der Verarbeitung der Frage: {str(e)}"

    def generate_random_question(self, question_type):
        # Zurücksetzen der ausgewählten Antworten
        self.current_question["selected_answers"] = []

        # Bestimme den Fragetyp-Code
        q_type_code = "mc" if "Multiple" in question_type else "sc"

        # Liste von möglichen Themen aus dem Hauptskript
        topics = ["Process Mining", "OLAP", "Data Warehouse", "ETL", "Business Intelligence",
                 "OLTP", "Dimensional Modeling", "Star Schema", "Snowflake Schema",
                 "Data Mart", "Fact Table", "Dimension Table", "KPI", "Dashboard"]

        # Zufälliges Thema auswählen
        random_topic = random.choice(topics)
        print(f"Generiere {q_type_code.upper()}-Frage zum Thema: {random_topic} in {self.question_language}")

        try:
            # Frage zum zufälligen Thema generieren
            question_data = self.generate_question_with_language(random_topic, q_type_code)

            if "error" in question_data:
                return question_data["error"], "", gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

            # Speichere die aktuelle Frage
            self.current_question["options"] = question_data["options"]
            self.current_question["correct_answers"] = self.tutor.last_correct_answers
            self.current_question["question_type"] = q_type_code

            # Formatiere die Ausgabe
            question_text = question_data["question_text"] + "\n\n"

            # Füge die Antwortoptionen zum Fragetext hinzu
            for key, value in question_data["options"].items():
                question_text += f"{key}) {value}\n"

            # Anpassen der Beschriftung je nach Sprache
            selected_label = "Ausgewählte Antworten: " if self.question_language == "de" else "Selected answers: "

            return question_text, "", gr.update(visible=True), gr.update(visible=True), selected_label
        except Exception as e:
            return f"Fehler bei der Fragen-Generierung: {str(e)}", "", gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

    def create_question(self, topic, question_type):
        # Zurücksetzen der ausgewählten Antworten
        self.current_question["selected_answers"] = []

        if not topic.strip():
            error_msg = "Bitte geben Sie ein Thema ein" if self.question_language == "de" else "Please enter a topic"
            return error_msg, "", gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

        # Bestimme den Fragetyp-Code
        q_type_code = "mc" if "Multiple" in question_type else "sc"

        try:
            # Frage zum angegebenen Thema generieren
            question_data = self.generate_question_with_language(topic, q_type_code)

            if "error" in question_data:
                return question_data["error"], "", gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

            # Speichere die aktuelle Frage
            self.current_question["options"] = question_data["options"]
            self.current_question["correct_answers"] = self.tutor.last_correct_answers
            self.current_question["question_type"] = q_type_code

            # Formatiere die Ausgabe
            question_text = question_data["question_text"] + "\n\n"

            # Füge die Antwortoptionen zum Fragetext hinzu
            for key, value in question_data["options"].items():
                question_text += f"{key}) {value}\n"

            # Anpassen der Beschriftung je nach Sprache
            selected_label = "Ausgewählte Antworten: " if self.question_language == "de" else "Selected answers: "

            return question_text, "", gr.update(visible=True), gr.update(visible=True), selected_label
        except Exception as e:
            return f"Fehler bei der Fragen-Generierung: {str(e)}", "", gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

    def generate_question_with_language(self, topic, question_type):
        """Generiert eine Frage in der ausgewählten Sprache"""
        # Hier fügen wir die Sprachinformation zum Thema hinzu
        if self.question_language == "en":
            # Für englische Fragen
            if question_type == "mc":
                prompt_type = "Multiple-choice question (multiple answers can be correct)"
            else:
                prompt_type = "Single-choice question (only one answer is correct)"

            # Generiere die Frage mit einem englischen Prompt
            doc = self.tutor.vectorstore.similarity_search(
                topic,
                k=2,
                filter={"source_type": "Hauptskript"}
            )[0]

            prompt = f"""
            Create a {prompt_type} about the topic: {topic}
            Based on this context: {doc.page_content}

            Give your answer in the following JSON format:
            {{
                "question": "The question here",
                "options": {{
                    "A": "Option A",
                    "B": "Option B",
                    "C": "Option C",
                    "D": "Option D"
                }},
                "correct_answers": ["A", "C"]  // For single-choice only one element, e.g. ["B"]
            }}

            The question should test understanding of the topic.
            """

            # Generiere die Antwort
            response = self.tutor.llm.invoke(prompt)

            # Parse die Antwort wie in der ursprünglichen Methode
            import json
            import re

            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return {"error": "Could not generate a valid question. Please try again."}

            try:
                json_str = json_match.group(0)
                question_data = json.loads(json_str)
                self.tutor.last_correct_answers = question_data["correct_answers"]
                return {
                    "question_text": question_data["question"],
                    "options": question_data["options"],
                    "source": {
                        "type": doc.metadata.get('source_type', 'Unknown'),
                        "file": doc.metadata.get('file_name', 'Unknown'),
                        "page": doc.metadata.get('page', 'Unknown')
                    }
                }
            except json.JSONDecodeError:
                return {"error": "Could not parse the JSON format correctly. Please try again."}

        else:
            # Für deutsche Fragen - verwende die ursprüngliche Methode
            return self.tutor.generate_question(topic, question_type)

    def toggle_answer(self, answer_key, current_selection):
        # Extrahiere die aktuell ausgewählten Antworten
        prefix = "Ausgewählte Antworten: " if self.question_language == "de" else "Selected answers: "
        if prefix in current_selection:
            current = current_selection.replace(prefix, "").strip()
            self.current_question["selected_answers"] = [a.strip() for a in current.split(",")] if current else []

        # Für Single Choice: Ersetze die Antwort
        if self.current_question.get("question_type") == "sc":
            self.current_question["selected_answers"] = [answer_key]
        else:
            # Für Multiple Choice: Toggle der Antwort
            if answer_key in self.current_question["selected_answers"]:
                self.current_question["selected_answers"].remove(answer_key)
            else:
                self.current_question["selected_answers"].append(answer_key)

        # Sortiere die Antworten
        self.current_question["selected_answers"].sort()

        # Aktualisiere die Anzeige
        return prefix + ", ".join(self.current_question["selected_answers"]) if self.current_question["selected_answers"] else prefix

    def check_answer(self):
        try:
            if not self.current_question["correct_answers"]:
                return "Bitte generiere zuerst eine Frage." if self.question_language == "de" else "Please generate a question first."

            if not self.current_question["selected_answers"]:
                return "Bitte wähle mindestens eine Antwort aus." if self.question_language == "de" else "Please select at least one answer."

            # Formatiere die Ausgabe
            if self.question_language == "de":
                result = f"Deine Antwort: {', '.join(self.current_question['selected_answers'])}\n"
                result += f"Richtige Antwort: {', '.join(self.current_question['correct_answers'])}\n\n"

                # Vergleiche die Antworten
                if set(self.current_question["selected_answers"]) == set(self.current_question["correct_answers"]):
                    result += "Richtig! 👍"
                else:
                    result += "Leider falsch. Versuche es noch einmal!"
            else:
                result = f"Your answer: {', '.join(self.current_question['selected_answers'])}\n"
                result += f"Correct answer: {', '.join(self.current_question['correct_answers'])}\n\n"

                # Vergleiche die Antworten
                if set(self.current_question["selected_answers"]) == set(self.current_question["correct_answers"]):
                    result += "Correct! 👍"
                else:
                    result += "Unfortunately wrong. Try again!"

            return result
        except Exception as e:
            error_msg = f"Fehler bei der Antwortprüfung: {str(e)}" if self.question_language == "de" else f"Error checking the answer: {str(e)}"
            return error_msg
