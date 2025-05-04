import gradio as gr
import random
from question_generator import QuestionGenerator
from answer_handler import AnswerHandler
from ui_components import create_tabs
from styles import get_css_styles
from utils import format_choices, get_question_type_code
from language_utils import get_error_message

class GradioInterface:
    def __init__(self, tutor):
        self.tutor = tutor
        self.current_question = {
            "options": {},
            "correct_answers": [],
            "selected_answers": []
        }
        self.question_language = "de"  
        self.attempt_count = 0  
        self.max_attempts = 3  
        self.question_queue = []  
        self.current_question_index = 0  
        self.total_questions = 0  
        self.active_output = "auto"
        self.question_generator = QuestionGenerator(self)
        self.answer_handler = AnswerHandler(self)

    def create_interface(self):
        with gr.Blocks(title="Business Software 2 Tutor") as demo:
            with gr.Row():
                with gr.Column(scale=8):
                    gr.Markdown("## Business Software 2 Tutor")
                with gr.Column(scale=1, min_width=80):
                    gr.Image(value="logo.png", show_label=False)
            gr.HTML(get_css_styles())

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
        self.active_output = "eigene" if topic else "auto"
        successful_questions = 0
        max_attempts = self.total_questions * 2
        attempts = 0

        while successful_questions < self.total_questions and attempts < max_attempts:
            attempts += 1
            try:
                if topic:
                    if not topic.strip():
                        error_msg = get_error_message(self.question_language, "empty_topic")
                        return error_msg, gr.update(visible=False), gr.update(choices=[]), "", 0, gr.update(visible=False), gr.update(visible=False)

                    q_type_code = get_question_type_code(question_type)

                    if successful_questions > 0:
                        current_topic = self.question_generator.generate_question_variation(
                            topic,
                            q_type_code,
                            self.question_queue
                        )
                    else:
                        current_topic = topic

                    print(f"Generiere Frage zu: {current_topic}")
                    question_data = self.question_generator.generate_question_with_language(
                        current_topic,
                        q_type_code
                    )

                    if "error" not in question_data and "options" in question_data and question_data["options"] and len(question_data["options"]) >= 2:
                        question_data["question_type"] = question_type
                        self.question_queue.append(question_data)
                        successful_questions += 1
                else:
                    question_data = self.question_generator.generate_random_question_internal(question_type)
                    if "options" in question_data and question_data["options"] and len(question_data["options"]) >= 2:
                        self.question_queue.append(question_data)
                        successful_questions += 1
            except Exception as e:
                print(f"Fehler bei der Fragengenerierung: {e}")
                continue

        self.total_questions = len(self.question_queue)

        if self.question_queue:
            question_data = self.question_queue[0]
            self.current_question["options"] = question_data["options"]
            self.current_question["correct_answers"] = self.tutor.last_correct_answers
            q_type = get_question_type_code(question_data.get("question_type", "Multiple Choice (MC)"))
            self.current_question["question_type"] = q_type

            progress = f"Frage 1 von {self.total_questions}" if self.question_language == "de" else f"Question 1 of {self.total_questions}"
            question_text = f"{progress}\n\n{question_data['question_text']}"

            choices = format_choices(question_data["options"])

            if self.active_output == "auto":
                return question_text, gr.update(visible=True), gr.update(choices=choices, value=[]), "", 0, gr.update(visible=True, value=progress), gr.update(visible=False)
            else:
                return question_text, gr.update(visible=True), gr.update(choices=choices, value=[]), "", 0, gr.update(visible=True, value=progress), gr.update(visible=False)
        else:
            error_msg = get_error_message(self.question_language, "question_generation")
            return error_msg, gr.update(visible=False), gr.update(choices=[]), "", 0, gr.update(visible=False), gr.update(visible=False)