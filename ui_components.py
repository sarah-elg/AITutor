import gradio as gr

def create_question_tab(interface):
    """Erstellt den Fragen-Tab"""
    components = {}

    gr.Markdown("Stellen Sie Ihre Fragen zum Business Software 2 Stoff")
    components["fragen_chat"] = gr.ChatInterface(
        interface.ask_question,
        examples=["Was ist Process Mining?", "Erkläre OLAP", "Was ist ein Data Warehouse?",
                 "What is Process Mining?", "Explain OLAP", "What is a Data Warehouse?"],
        title="Business Software 2 Fragen"
    )

    return components

def create_trainer_tab(interface):
    """Erstellt den Trainer-Tab mit allen Komponenten"""
    components = {}

    # Umschalter-Buttons für Fragetypen
    with gr.Row(equal_height=True):
        components["auto_btn"] = gr.Button("Automatische Fragen", size="lg", variant="primary")
        components["eigene_btn"] = gr.Button("Eigene Fragen", size="lg")

    # Sprachauswahl für Fragen
    with gr.Row():
        components["question_language"] = gr.Radio(
            ["Deutsch", "English"],
            value="Deutsch",
            label="Sprache für Fragen / Language for questions"
        )

    # Automatische Fragen-Bereich
    with gr.Column(visible=True) as auto_fragen_bereich:
        gr.Markdown("### Automatische Fragen")
        gr.Markdown("Lassen Sie sich automatisch Fragen generieren")

        # Fragetyp für automatische Fragen
        components["auto_question_type"] = gr.Radio(
            ["Multiple Choice (MC)", "Single Choice (SC)"],
            value="Multiple Choice (MC)",
            label="Fragetyp"
        )

        # Anzahl der Fragen
        components["question_count"] = gr.Slider(
            minimum=1,
            maximum=5,
            value=3,
            step=1,
            label="Anzahl der Fragen"
        )

        # Fortschrittsanzeige
        components["progress_display"] = gr.Markdown("", visible=False)

        components["auto_question_btn"] = gr.Button("Neue Fragen generieren")
        components["auto_question_output"] = gr.Markdown("Klicken Sie auf 'Neue Fragen generieren', um Fragen zu erstellen")

    # Eigene Fragen-Bereich
    with gr.Column(visible=False) as eigene_fragen_bereich:
        gr.Markdown("### Eigene Fragen")
        gr.Markdown("Erstellen Sie eigene Fragen zu einem bestimmten Thema")

        # Eingabefeld für das Thema
        components["eigene_topic"] = gr.Textbox(
            placeholder="Geben Sie ein Thema ein (z.B. 'Process Mining')",
            label="Thema"
        )

        # Fragetyp für eigene Fragen
        components["eigene_type"] = gr.Radio(
            ["Multiple Choice (MC)", "Single Choice (SC)"],
            value="Multiple Choice (MC)",
            label="Fragetyp"
        )

        # Anzahl der Fragen für eigene Fragen
        components["eigene_question_count"] = gr.Slider(
            minimum=1,
            maximum=5,
            value=3,
            step=1,
            label="Anzahl der Fragen"
        )

        # Fortschrittsanzeige für eigene Fragen
        components["eigene_progress_display"] = gr.Markdown("", visible=False)

        components["eigene_question_btn"] = gr.Button("Fragen erstellen")
        components["eigene_question_output"] = gr.Markdown("Hier erscheinen Ihre Fragen")

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
        components["options"] = gr.CheckboxGroup(choices=[], label="", interactive=True)
        components["check_btn"] = gr.Button("Antwort prüfen")
        components["next_btn"] = gr.Button("Nächste Frage", visible=False)
        components["result"] = gr.Markdown("")
        components["attempt_counter"] = gr.Number(value=0, visible=False)

    components["auto_fragen_bereich"] = auto_fragen_bereich
    components["eigene_fragen_bereich"] = eigene_fragen_bereich
    components["answer_group"] = answer_group

    return components

def create_tabs(interface):
    """Erstellt die Tab-Struktur und gibt alle UI-Komponenten zurück"""
    components = {}

    with gr.Tabs() as tabs:
        # Tab 1: Fragen-Modus
        with gr.TabItem("Fragen"):
            components.update(create_question_tab(interface))

        # Tab 2: Trainer
        with gr.TabItem("Trainer"):
            components.update(create_trainer_tab(interface))

    # Event-Handler registrieren
    register_event_handlers(interface, components)

    return components

def register_event_handlers(interface, components):
    """Registriert alle Event-Handler für die UI-Komponenten"""

    # Umschaltfunktionen für die Buttons
    def show_auto_fragen():
        interface.active_output = "auto"
        return gr.update(visible=True), gr.update(visible=False), gr.update(variant="primary"), gr.update(variant="secondary")

    def show_eigene_fragen():
        interface.active_output = "eigene"
        return gr.update(visible=False), gr.update(visible=True), gr.update(variant="secondary"), gr.update(variant="primary")

    # Event-Handler für die Umschaltbuttons
    components["auto_btn"].click(
        show_auto_fragen,
        outputs=[
            components["auto_fragen_bereich"],
            components["eigene_fragen_bereich"],
            components["auto_btn"],
            components["eigene_btn"]
        ]
    )

    components["eigene_btn"].click(
        show_eigene_fragen,
        outputs=[
            components["auto_fragen_bereich"],
            components["eigene_fragen_bereich"],
            components["auto_btn"],
            components["eigene_btn"]
        ]
    )

    # Event-Handler für Sprachauswahl
    components["question_language"].change(
        interface.set_question_language,
        inputs=[components["question_language"]]
    )

    # Event-Handler für automatische Fragen
    components["auto_question_btn"].click(
        lambda q_type, count: interface.generate_questions(q_type, count),
        inputs=[components["auto_question_type"], components["question_count"]],
        outputs=[
            components["auto_question_output"],
            components["answer_group"],
            components["options"],
            components["result"],
            components["attempt_counter"],
            components["progress_display"],
            components["next_btn"]
        ]
    )

    # Event-Handler für eigene Fragen
    components["eigene_question_btn"].click(
        lambda topic, q_type, count: interface.generate_questions(q_type, count, topic),
        inputs=[components["eigene_topic"], components["eigene_type"], components["eigene_question_count"]],
        outputs=[
            components["eigene_question_output"],
            components["answer_group"],
            components["options"],
            components["result"],
            components["attempt_counter"],
            components["eigene_progress_display"],
            components["next_btn"]
        ]
    )

    # Handler für den Prüfen-Button
    components["check_btn"].click(
        interface.answer_handler.check_answer_with_attempts,
        inputs=[components["options"], components["attempt_counter"]],
        outputs=[components["result"], components["attempt_counter"], components["next_btn"]]
    )

    # Handler für den Nächste-Frage-Button
    components["next_btn"].click(
        interface.answer_handler.handle_next_question,
        outputs=[
            components["auto_question_output"],
            components["eigene_question_output"],
            components["answer_group"],
            components["options"],
            components["result"],
            components["attempt_counter"],
            components["progress_display"],
            components["eigene_progress_display"],
            components["next_btn"]
        ]
    )