import gradio as gr
from utils import format_choices, get_question_type_code, format_progress_text, get_end_message

class AnswerHandler:
    def __init__(self, interface):
        self.interface = interface

    def handle_next_question(self):
        """Handler für den Nächste-Frage-Button, der die richtige Ausgabe aktualisiert"""
        self.interface.current_question_index += 1

        # Hole die aktuelle Frage
        if self.interface.current_question_index >= len(self.interface.question_queue):
            message = get_end_message(self.interface.question_language)

            # Wenn alle Fragen beantwortet wurden, zeige die Nachricht in beiden Ausgabefeldern an
            if self.interface.active_output == "auto":
                return message, "", gr.update(visible=False), gr.update(choices=[]), "", 0, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
            else:
                return "", message, gr.update(visible=False), gr.update(choices=[]), "", 0, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

        question_data = self.interface.question_queue[self.interface.current_question_index]

        # Setze die aktuelle Frage
        self.interface.current_question["options"] = question_data["options"]
        self.interface.current_question["correct_answers"] = self.interface.tutor.last_correct_answers
        q_type = get_question_type_code(question_data.get("question_type", "Multiple Choice (MC)"))
        self.interface.current_question["question_type"] = q_type

        # Zurücksetzen des Versuchszählers für die neue Frage
        self.interface.attempt_count = 0

        # Fortschrittsanzeige
        progress = format_progress_text(
            self.interface.current_question_index + 1,
            self.interface.total_questions,
            self.interface.question_language
        )
        question_text = f"{progress}\n\n{question_data['question_text']}"

        choices = format_choices(question_data["options"])

        # Bestimme, welches Ausgabefeld aktualisiert werden soll
        if self.interface.active_output == "auto":
            return question_text, "", gr.update(visible=True), gr.update(choices=choices, value=[]), "", 0, gr.update(visible=True, value=progress), gr.update(visible=False), gr.update(visible=False)
        else:
            return "", question_text, gr.update(visible=True), gr.update(choices=choices, value=[]), "", 0, gr.update(visible=False), gr.update(visible=True, value=progress), gr.update(visible=False)

    def check_answer_with_attempts(self, selected, current_attempts):
        """Prüft die Antwort und wechselt zur nächsten Frage, wenn richtig oder max. Versuche erreicht"""
        # selected ist eine Liste wie ["A) Star schema", ...]
        selected_keys = [s.split(")")[0] for s in selected]
        self.interface.attempt_count = int(current_attempts) + 1
        is_correct = set(selected_keys) == set(self.interface.current_question["correct_answers"])

        # Prüfe, ob wir zur nächsten Frage wechseln sollten
        move_to_next = is_correct or self.interface.attempt_count >= self.interface.max_attempts

        # Formatiere Ausgabe je nach Sprache
        result = self._format_result_message(selected_keys, is_correct)

        # Zeige den "Nächste Frage"-Button, wenn wir zur nächsten Frage wechseln sollten
        show_next = move_to_next and (self.interface.current_question_index + 1) < len(self.interface.question_queue)

        return result, self.interface.attempt_count, gr.update(visible=show_next)

    def _format_result_message(self, selected_keys, is_correct):
        """Formatiert die Ergebnismeldung basierend auf der Antwort"""
        if self.interface.question_language == "de":
            result = f"Deine Antwort: {', '.join(selected_keys) if selected_keys else 'Keine Auswahl'}\n"
            if is_correct:
                result += "Richtig! 👍"
            elif self.interface.attempt_count >= self.interface.max_attempts:
                result += f"Richtige Antwort: {', '.join(self.interface.current_question['correct_answers'])}\n\n"
                result += "Leider falsch."
            else:
                result += f"Leider falsch. Versuch {self.interface.attempt_count}/{self.interface.max_attempts}!"
        else:
            result = f"Your answer: {', '.join(selected_keys) if selected_keys else 'No selection'}\n"
            if is_correct:
                result += "Correct! 👍"
            elif self.interface.attempt_count >= self.interface.max_attempts:
                result += f"Correct answer: {', '.join(self.interface.current_question['correct_answers'])}\n\n"
                result += "Unfortunately wrong."
            else:
                result += f"Unfortunately wrong. Attempt {self.interface.attempt_count}/{self.interface.max_attempts}!"

        # Füge Hinweis zur nächsten Frage hinzu, wenn wir wechseln sollten
        move_to_next = is_correct or self.interface.attempt_count >= self.interface.max_attempts
        if move_to_next:
            next_index = self.interface.current_question_index + 1
            if next_index < len(self.interface.question_queue):
                if self.interface.question_language == "de":
                    result += "\n\nKlicke auf 'Nächste Frage', um fortzufahren..."
                else:
                    result += "\n\nClick 'Next Question' to continue..."
            else:
                if self.interface.question_language == "de":
                    result += "\n\nAlle Fragen beantwortet! Sie können neue Fragen generieren."
                else:
                    result += "\n\nAll questions answered! You can generate new questions."

        return result