
import gradio as gr
import random

# Globale Variable für die aktuelle Frage
current_question = {
    "options": {},
    "correct_answers": [],
    "selected_answers": []
}

class GradioInterface:
    def __init__(self, tutor):
        self.tutor = tutor
        self.current_question = {
            "options": {},
            "correct_answers": [],
            "selected_answers": []
        }

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
                        examples=["Was ist Process Mining?", "Erkläre OLAP", "Was ist ein Data Warehouse?"],
                        title="BS2 Fragen"
                    )

                # Tab 2: Automatischer Fragen-Modus
                with gr.TabItem("Kurs Trainer"):
                    gr.Markdown("Automatische Fragen")

                    # Auswahl des Fragetyps
                    auto_question_type = gr.Radio(
                        ["Multiple Choice (MC)", "Single Choice (SC)"],
                        value="Multiple Choice (MC)",
                        label="Fragetyp"
                    )

                    auto_question_btn = gr.Button("Neue Frage")
                    auto_question_output = gr.Markdown("Klicken Sie auf 'Neue Frage', um eine Frage zu generieren")

                    # Antwortbuttons - UNTEREINANDER angeordnet
                    with gr.Group(visible=False) as auto_buttons_group:
                        gr.Markdown("### Wähle die richtige(n) Antwort(en):")

                        # Jeder Button in einer eigenen Zeile
                        auto_btn_a = gr.Button("A", scale=1)
                        auto_btn_b = gr.Button("B", scale=1)
                        auto_btn_c = gr.Button("C", scale=1)
                        auto_btn_d = gr.Button("D", scale=1)

                        # Ausgewählte Antworten anzeigen
                        auto_selected = gr.Markdown("Ausgewählte Antworten: ")

                    # Button zum Überprüfen der Antwort
                    auto_check_btn = gr.Button("Antwort prüfen", visible=False)
                    auto_result = gr.Markdown("")

                    # Event-Handler
                    auto_question_btn.click(
                        self.update_auto_question,
                        inputs=[auto_question_type],
                        outputs=[auto_question_output, auto_buttons_group, auto_check_btn, auto_selected]
                    )

                    # Handler für die Antwortbuttons
                    auto_btn_a.click(lambda s: self.toggle_answer("A", s), inputs=[auto_selected], outputs=[auto_selected])
                    auto_btn_b.click(lambda s: self.toggle_answer("B", s), inputs=[auto_selected], outputs=[auto_selected])
                    auto_btn_c.click(lambda s: self.toggle_answer("C", s), inputs=[auto_selected], outputs=[auto_selected])
                    auto_btn_d.click(lambda s: self.toggle_answer("D", s), inputs=[auto_selected], outputs=[auto_selected])

                    # Handler für den Prüfen-Button
                    auto_check_btn.click(self.check_answer, outputs=[auto_result])

                # Tab 3: Eigener Fragen-Modus
                with gr.TabItem("Eigene Trainer"):
                    gr.Markdown("Erstellen Sie eigene Fragen zu einem bestimmten Thema")

                    # Eingabefeld für das Thema und Auswahl des Fragetyps
                    eigene_topic = gr.Textbox(
                        placeholder="Geben Sie ein Thema ein (z.B. 'Process Mining')",
                        label="Thema"
                    )
                    eigene_type = gr.Radio(
                        ["Multiple Choice (MC)", "Single Choice (SC)"],
                        value="Multiple Choice (MC)",
                        label="Fragetyp"
                    )

                    eigene_question_btn = gr.Button("Frage erstellen")
                    eigene_question_output = gr.Markdown("Hier erscheint Ihre Frage")

                    # Antwortbuttons - UNTEREINANDER angeordnet
                    with gr.Group(visible=False) as eigene_buttons_group:
                        gr.Markdown("### Wähle die richtige(n) Antwort(en):")

                        # Jeder Button in einer eigenen Zeile
                        eigene_btn_a = gr.Button("A", scale=1)
                        eigene_btn_b = gr.Button("B", scale=1)
                        eigene_btn_c = gr.Button("C", scale=1)
                        eigene_btn_d = gr.Button("D", scale=1)

                        # Ausgewählte Antworten anzeigen
                        eigene_selected = gr.Markdown("Ausgewählte Antworten: ")

                    # Button zum Überprüfen der Antwort
                    eigene_check_btn = gr.Button("Antwort prüfen", visible=False)
                    eigene_result = gr.Markdown("")

                    # Event-Handler
                    eigene_question_btn.click(
                        self.update_eigene_question,
                        inputs=[eigene_topic, eigene_type],
                        outputs=[eigene_question_output, eigene_buttons_group, eigene_check_btn, eigene_selected]
                    )

                    # Handler für die Antwortbuttons
                    eigene_btn_a.click(lambda s: self.toggle_answer("A", s), inputs=[eigene_selected], outputs=[eigene_selected])
                    eigene_btn_b.click(lambda s: self.toggle_answer("B", s), inputs=[eigene_selected], outputs=[eigene_selected])
                    eigene_btn_c.click(lambda s: self.toggle_answer("C", s), inputs=[eigene_selected], outputs=[eigene_selected])
                    eigene_btn_d.click(lambda s: self.toggle_answer("D", s), inputs=[eigene_selected], outputs=[eigene_selected])

                    # Handler für den Prüfen-Button
                    eigene_check_btn.click(self.check_answer, outputs=[eigene_result])

        return demo

    def ask_question(self, message, history):
        try:
            response = self.tutor.ask_question(message)
            return response
        except Exception as e:
            return f"Fehler bei der Verarbeitung der Frage: {str(e)}"

    def generate_random_question(self, question_type="mc"):
        # Zurücksetzen der ausgewählten Antworten
        self.current_question["selected_answers"] = []

        # Liste von möglichen Themen aus dem Hauptskript
        topics = ["Process Mining", "OLAP", "Data Warehouse", "ETL", "Business Intelligence",
                "OLTP", "Dimensional Modeling", "Star Schema", "Snowflake Schema",
                "Data Mart", "Fact Table", "Dimension Table", "KPI", "Dashboard"]

        # Zufälliges Thema auswählen
        random_topic = random.choice(topics)
        print(f"Generiere {question_type.upper()}-Frage zum Thema: {random_topic}")

        try:
            # Frage zum zufälligen Thema generieren
            question_data = self.tutor.generate_question(random_topic, question_type)

            if "error" in question_data:
                return question_data["error"], gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

            # Speichere die aktuelle Frage
            self.current_question["options"] = question_data["options"]
            self.current_question["correct_answers"] = self.tutor.last_correct_answers
            self.current_question["question_type"] = question_type

            # Formatiere die Ausgabe
            question_text = question_data["question_text"] + "\n\n"

            # Füge die Antwortoptionen zum Fragetext hinzu
            for key, value in question_data["options"].items():
                question_text += f"{key}) {value}\n"

            return question_text, gr.update(visible=True), gr.update(visible=True), "Ausgewählte Antworten: "
        except Exception as e:
            return f"Fehler bei der Fragen-Generierung: {str(e)}", gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

    def create_question(self, topic, question_type="mc"):
        # Zurücksetzen der ausgewählten Antworten
        self.current_question["selected_answers"] = []

        if not topic.strip():
            return "Bitte geben Sie ein Thema ein", gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

        try:
            # Frage zum angegebenen Thema generieren
            question_data = self.tutor.generate_question(topic, question_type)

            if "error" in question_data:
                return question_data["error"], gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

            # Speichere die aktuelle Frage
            self.current_question["options"] = question_data["options"]
            self.current_question["correct_answers"] = self.tutor.last_correct_answers
            self.current_question["question_type"] = question_type

            # Formatiere die Ausgabe
            question_text = question_data["question_text"] + "\n\n"

            # Füge die Antwortoptionen zum Fragetext hinzu
            for key, value in question_data["options"].items():
                question_text += f"{key}) {value}\n"

            return question_text, gr.update(visible=True), gr.update(visible=True), "Ausgewählte Antworten: "
        except Exception as e:
            return f"Fehler bei der Fragen-Generierung: {str(e)}", gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

    def toggle_answer(self, answer_key, current_selection):
        # Extrahiere die aktuell ausgewählten Antworten
        if "Ausgewählte Antworten: " in current_selection:
            current = current_selection.replace("Ausgewählte Antworten: ", "").strip()
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
        return "Ausgewählte Antworten: " + ", ".join(self.current_question["selected_answers"]) if self.current_question["selected_answers"] else "Ausgewählte Antworten: "

    def check_answer(self):
        try:
            if not self.current_question["correct_answers"]:
                return "Bitte generiere zuerst eine Frage."

            if not self.current_question["selected_answers"]:
                return "Bitte wähle mindestens eine Antwort aus."

            # Formatiere die Ausgabe
            result = f"Deine Antwort: {', '.join(self.current_question['selected_answers'])}\n"
            result += f"Richtige Antwort: {', '.join(self.current_question['correct_answers'])}\n\n"

            # Vergleiche die Antworten
            if set(self.current_question["selected_answers"]) == set(self.current_question["correct_answers"]):
                result += "Richtig! 👍"
            else:
                result += "Leider falsch. Versuche es noch einmal!"

            return result
        except Exception as e:
            return f"Fehler bei der Antwortprüfung: {str(e)}"

    def update_auto_question(self, q_type):
        q_type_code = "mc" if "Multiple" in q_type else "sc"
        question_text, buttons_visible, check_visible, selected = self.generate_random_question(q_type_code)
        return question_text, buttons_visible, check_visible, selected

    def update_eigene_question(self, topic, q_type):
        if not topic.strip():
            return "Bitte geben Sie ein Thema ein", gr.update(visible=False), gr.update(visible=False), "Ausgewählte Antworten: "

        q_type_code = "mc" if "Multiple" in q_type else "sc"
        question_text, buttons_visible, check_visible, selected = self.create_question(topic, q_type_code)
        return question_text, buttons_visible, check_visible, selected
