from langchain_ollama import OllamaLLM
from language_utils import detect_language, format_response_by_language
from prompts import get_answer_prompt

class OptimizedBS2Tutor:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = OllamaLLM(model="llama3.2", temperature=0.0)
        self.last_correct_answers = []

    def ask_question(self, question, k=5):
        """
        Beantwortet eine Frage basierend auf dem Hauptskript
        """
        try:
            language = detect_language(question)

            main_docs = self.vectorstore.similarity_search(
                question,
                k=k,
                filter={"source_type": "Hauptskript"}
            )
            print(f"Gefunden: {len(main_docs)} relevante Dokumente im Hauptskript")
            print("Generiere Antwort basierend auf Hauptskript...")
            answer, detected_language = self._generate_answer(question, main_docs)
            print("Antwort generiert!")

            return self._format_response(answer, detected_language, main_docs, "Hauptskript")

        except Exception as e:
            return f"Fehler bei der Verarbeitung der Frage: {str(e)}"

    def _generate_answer(self, question, documents):
        """Generiert eine Antwort basierend auf den relevanten Dokumenten"""
        language = detect_language(question)
        prompt = get_answer_prompt(language, question, documents)
        answer = self.llm.invoke(prompt)
        return answer, language

    def _format_response(self, answer, language, documents, source_label):
        """Formatiert die Antwort mit Quellenangaben"""
        return format_response_by_language(language, answer, documents, source_label)

    def generate_question(self, topic, question_type, language):
        """
        Delegiert die Fragengenerierung an den QuestionGenerator
        """
        from question_generator import QuestionGenerator

        class TempInterface:
            def __init__(self, tutor, language):
                self.tutor = tutor
                self.question_language = language
                self.current_question = {
                    "options": {},
                    "correct_answers": [],
                    "selected_answers": []
                }

        temp_interface = TempInterface(self, language)
        generator = QuestionGenerator(temp_interface)
        return generator.generate_question_with_language(topic, question_type)