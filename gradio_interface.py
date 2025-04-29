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
        self.attempt_count = 0  # Zähler für Antwortversuche
        self.max_attempts = 3  # Maximale Anzahl von Versuchen

    def create_interface(self):
        # Hauptfunktion für das Gradio-Interface
        with gr.Blocks(title="Business Software 2 Tutor") as demo:
            gr.Markdown("# Business Software 2 Tutor")
            gr.HTML(
            """
            <style>
            button.selected[role="tab"][aria-selected="true"] {
                background: #005CA9 !important;
                color: #fff !important;
                border-radius: 12px 12px 0 0 !important;
                border: 2px solid #005CA9 !important;
                font-weight: bold !important;
                box-shadow: 0 2px 8px #005ca93a;
                border-bottom: none !important;
                position: relative;
            }
            button.selected[role="tab"][aria-selected="true"]::after {
                content: none !important;
                display: none !important;
                background: none !important;
                border: none !important;
            }
            button[role="tab"]:not(.selected)[aria-selected="false"] {
                background: #E6F0FA !important;
                color: #005CA9 !important;
                border-radius: 12px 12px 0 0 !important;
                border: 2px solid #E6F0FA !important;
                margin-right: 4px !important;
                font-weight: normal !important;
            }
            button[role="tab"] {
                font-size: 1.1em !important;
                padding: 8px 24px !important;
            }
            button.primary, button[variant="primary"] {
                background: #005CA9 !important;
                color: #fff !important;
                border: 2px solid #005CA9 !important;
                font-weight: bold !important;
                border-radius: 10px !important;
                box-shadow: 0 2px 8px #005ca93a;
                transition: background 0.2s, color 0.2s;
            }
            button.primary:hover, button[variant="primary"]:hover {
                background: #003366 !important;
                border-color: #003366 !important;
            }
            button:not(.primary):not([variant="primary"]) {
                background: #E6F0FA !important;
                color: #005CA9 !important;
                border: 2px solid #E6F0FA !important;
                font-weight: normal !important;
                border-radius: 10px !important;
            }
            input[type="radio"]:checked + label {
                color: #fff !important;
                background: #005CA9 !important;
                border-color: #005CA9 !important;
            }
            input[type="radio"] + label {
                color: #005CA9 !important;
                background: #E6F0FA !important;
                border: 2px solid #E6F0FA !important;
                border-radius: 8px !important;
                padding: 6px 16px !important;
                margin-right: 8px !important;
                font-weight: normal !important;
                transition: background 0.2s, color 0.2s;
            }
            input[type="radio"]:checked + label {
                font-weight: bold !important;
            }
            input[type="radio"]:checked {
                accent-color: #005CA9 !important;
            }
             input[type="checkbox"]:checked {
                accent-color: #005CA9 !important;
            }       

            .svelte-drgfj2 .example, .svelte-1ipelgc .example, .svelte-1tcem6n .example {
                background: #E6F0FA !important;
                color: #005CA9 !important;
                border: 1.5px solid #005CA9 !important;
                font-weight: bold !important;
                border-radius: 10px !important;
                transition: background 0.2s, color 0.2s;
            }
            .svelte-drgfj2 .example.selected,
            .svelte-1ipelgc .example.selected,
            .svelte-1tcem6n .example.selected,
            .svelte-drgfj2 .example:active,
            .svelte-1ipelgc .example:active,
            .svelte-1tcem6n .example:active {
                background: #005CA9 !important;
                color: #fff !important;
                border-color: #005CA9 !important;
            }
            </style>
            """
        )          

            with gr.Tabs() as tabs:
                # Tab 1: Fragen-Modus
                with gr.TabItem("Fragen"):
                    gr.Markdown("Stellen Sie Ihre Fragen zum Business Software 2 Stoff")
                    fragen_chat = gr.ChatInterface(
                        self.ask_question,
                        examples=["Was ist Process Mining?", "Erkläre OLAP", "Was ist ein Data Warehouse?",
                                 "What is Process Mining?", "Explain OLAP", "What is a Data Warehouse?"],
                        title="Business Software 2 Fragen"
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

                    # Gemeinsame Antwortoptionen-Gruppe (wird für beide Fragetypen verwendet)
                    with gr.Group(visible=False) as answer_group:
                        gr.Markdown("### Wähle die richtige(n) Antwort(en):")
                        gr.HTML(
                             """
                            <style>
                            .gr-checkbox-group {
                                display: flex !important;
                                flex-direction: column !important;
                            }
                            .gr-checkbox-group label {
                                display: block !important;
                                margin-bottom: 8px !important;
                                width: 100% !important;
                            }
                            </style>
                            """
                        )
                        options = gr.CheckboxGroup(choices=[], label="", interactive=True)
                        check_btn = gr.Button("Antwort prüfen")
                        result = gr.Markdown("")
                        attempt_counter = gr.Number(value=0, visible=False)

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
                    def generate_random_question_with_options(question_type):
                        self.attempt_count = 0
                        question_data = self.generate_random_question_internal(question_type)
                        choices = [f"{k}) {v}" for k, v in question_data["options"].items()]
                        return [
                            question_data["question_text"],  # Frage
                            gr.update(visible=True),         # Zeige Antwortgruppe
                            gr.update(choices=choices, value=[]),  # Setze die neuen Optionen
                            "",  # Ergebnis leeren
                            0    # Versuchszähler zurücksetzen
                        ]

                    auto_question_btn.click(
                        generate_random_question_with_options,
                        inputs=[auto_question_type],
                        outputs=[
                            auto_question_output,
                            answer_group,
                            options,
                            result,
                            attempt_counter
                        ]
                    )

                    # Event-Handler für eigene Fragen
                    def create_question_with_options(topic, q_type):
                        self.attempt_count = 0
                        question_data = self.create_question_internal(topic, q_type)
                        choices = [f"{k}) {v}" for k, v in question_data["options"].items()]
                        return [
                            question_data["question_text"],
                            gr.update(visible=True),
                            gr.update(choices=choices, value=[]),
                            "",
                            0
                        ]

                    eigene_question_btn.click(
                        create_question_with_options,
                        inputs=[eigene_topic, eigene_type],
                        outputs=[
                            eigene_question_output,
                            answer_group,
                            options,
                            result,
                            attempt_counter
                        ]
                    )

                    # Handler für den Prüfen-Button
                    def check_answer_with_attempts(selected, current_attempts):
                        # selected ist eine Liste wie ["A) Star schema", ...]
                        selected_keys = [s.split(")")[0] for s in selected]
                        self.attempt_count = int(current_attempts) + 1
                        is_correct = set(selected_keys) == set(self.current_question["correct_answers"])

                        # Formatiere Ausgabe je nach Sprache
                        if self.question_language == "de":
                            result = f"Deine Antwort: {', '.join(selected_keys) if selected_keys else 'Keine Auswahl'}\n"
                            if is_correct:
                                result += "Richtig! 👍"
                            elif self.attempt_count >= self.max_attempts:
                                result += f"Richtige Antwort: {', '.join(self.current_question['correct_answers'])}\n\n"
                                result += "Leider falsch. Versuche es mit einer neuen Frage!"
                            else:
                                result += f"Leider falsch. Versuch {self.attempt_count}/{self.max_attempts}!"
                        else:
                            result = f"Your answer: {', '.join(selected_keys) if selected_keys else 'No selection'}\n"
                            if is_correct:
                                result += "Correct! 👍"
                            elif self.attempt_count >= self.max_attempts:
                                result += f"Correct answer: {', '.join(self.current_question['correct_answers'])}\n\n"
                                result += "Unfortunately wrong. Try a new question!"
                            else:
                                result += f"Unfortunately wrong. Attempt {self.attempt_count}/{self.max_attempts}!"

                        return result, self.attempt_count

                    check_btn.click(
                        check_answer_with_attempts,
                        inputs=[options, attempt_counter],
                        outputs=[result, attempt_counter]
                    )

        return demo

    # Interne Methoden für die Fragengenerierung
    def generate_random_question_internal(self, question_type):
        q_type_code = "mc" if "Multiple" in question_type else "sc"
        topics = ["Process Mining", "OLAP", "Data Warehouse", "ETL", "Business Intelligence",
                 "OLTP", "Dimensional Modeling", "Star Schema", "Snowflake Schema",
                 "Data Mart", "Fact Table", "Dimension Table", "KPI", "Dashboard"]
        random_topic = random.choice(topics)
        try:
            question_data = self.generate_question_with_language(random_topic, q_type_code)
            if "error" in question_data:
                return {"question_text": question_data["error"], "options": {}}
            self.current_question["options"] = question_data["options"]
            self.current_question["correct_answers"] = self.tutor.last_correct_answers
            self.current_question["question_type"] = q_type_code
            return {"question_text": question_data["question_text"], "options": question_data["options"]}
        except Exception as e:
            return {"question_text": f"Fehler bei der Fragen-Generierung: {str(e)}", "options": {}}

    def create_question_internal(self, topic, question_type):
        if not topic.strip():
            error_msg = "Bitte geben Sie ein Thema ein" if self.question_language == "de" else "Please enter a topic"
            return {"question_text": error_msg, "options": {}}
        q_type_code = "mc" if "Multiple" in question_type else "sc"
        try:
            question_data = self.generate_question_with_language(topic, q_type_code)
            if "error" in question_data:
                return {"question_text": question_data["error"], "options": {}}
            self.current_question["options"] = question_data["options"]
            self.current_question["correct_answers"] = self.tutor.last_correct_answers
            self.current_question["question_type"] = q_type_code
            return {"question_text": question_data["question_text"], "options": question_data["options"]}
        except Exception as e:
            return {"question_text": f"Fehler bei der Fragen-Generierung: {str(e)}", "options": {}}

    def set_question_language(self, language):
        self.question_language = "de" if language == "Deutsch" else "en"
        return None

    def ask_question(self, message, history):
        try:
            response = self.tutor.ask_question(message)
            return response
        except Exception as e:
            return f"Fehler bei der Verarbeitung der Frage: {str(e)}"

    def generate_question_with_language(self, topic, question_type):
        if self.question_language == "en":
            if question_type == "mc":
                prompt_type = "Multiple-choice question (multiple answers can be correct)"
            else:
                prompt_type = "Single-choice question (only one answer is correct)"
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
            response = self.tutor.llm.invoke(prompt)
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
            return self.tutor.generate_question(topic, question_type)