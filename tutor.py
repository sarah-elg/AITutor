from langchain_ollama import OllamaLLM
from language_utils import detect_language, get_prompt_by_language, format_response_by_language, is_insufficient_answer

class OptimizedBS2Tutor:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = OllamaLLM(model="llama3.2", temperature=0.0)
        self.last_correct_answers = []  # Für die Fragen-Generierung

    def ask_question(self, question, k=5, use_main_script_first=True):
        """
        Beantwortet eine Frage basierend auf dem Hauptskript und der Literatur
        """
        try:
            # Erkenne die Sprache der Frage
            language = detect_language(question)

            # 1. Suche zuerst im Hauptskript, wenn gewünscht
            if use_main_script_first:
                # Suche mit Metadaten-Filter für Hauptskript
                main_docs = self.vectorstore.similarity_search(
                    question,
                    k=k,
                    filter={"source_type": "Hauptskript"}
                )
                print(f"Gefunden: {len(main_docs)} relevante Dokumente im Hauptskript")

                # Wenn genügend relevante Dokumente im Hauptskript gefunden wurden
                if len(main_docs) >= 2:
                    print("Generiere Antwort basierend auf Hauptskript...")
                    answer, detected_language = self._generate_answer(question, main_docs)
                    print("Antwort generiert!")

                    # Prüfe, ob die Antwort ausreichend ist
                    if not is_insufficient_answer(answer, detected_language):
                        return self._format_response(answer, detected_language, main_docs, "Hauptskript")

            # 2. Suche in allen Dokumenten (Hauptskript + Literatur)
            print("Suche in allen Dokumenten...")
            all_docs = self.vectorstore.similarity_search(question, k=k)
            print(f"Gefunden: {len(all_docs)} relevante Dokumente insgesamt")

            print("Generiere Antwort basierend auf allen Quellen...")
            answer, detected_language = self._generate_answer(question, all_docs)
            print("Antwort generiert!")

            return self._format_response(answer, detected_language, all_docs, "Alle Quellen")

        except Exception as e:
            return f"Fehler bei der Verarbeitung der Frage: {e}"

    def _generate_answer(self, question, documents):
        """Generiert eine Antwort basierend auf den relevanten Dokumenten"""
        # Erkenne die Sprache der Frage
        language = detect_language(question)

        # Erstelle den Prompt basierend auf der erkannten Sprache
        prompt = get_prompt_by_language(language, question, documents)

        # Generiere Antwort
        answer = self.llm.invoke(prompt)
        return answer, language

    def _format_response(self, answer, language, documents, source_label):
        """Formatiert die Antwort mit Quellenangaben"""
        # Formatiere die Antwort basierend auf der erkannten Sprache
        return format_response_by_language(language, answer, documents, source_label)

    def generate_mc_question(self, topic):
        """Generiert eine Multiple-Choice-Frage zum angegebenen Thema"""

        # 1. Relevante Dokumente zum Thema finden
        relevant_docs = self.vectorstore.similarity_search(
            topic,
            k=2,
            filter={"source_type": "Hauptskript"}  # Bevorzuge Hauptskript für MC-Fragen
        )

        if not relevant_docs:
            return "Ich konnte keine relevanten Informationen für eine Frage finden."

        # 2. Prompt für MC-Frage
        doc = relevant_docs[0]
        prompt = f"""
        Erstelle eine Multiple-Choice-Frage zum Thema: {topic}
        Basierend auf diesem Kontext: {doc.page_content}
        Format:
        Frage: [Frage]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Richtige Antwort: [A/B/C/D]
        Die Frage sollte das Verständnis des Themas testen.
        """
        # 3. Frage generieren
        question = self.llm.invoke(prompt)
        # 4. Formatierte Ausgabe
        source_type = doc.metadata.get('source_type', 'Unbekannt')
        file_name = doc.metadata.get('file_name', 'Unbekannt')
        page = doc.metadata.get('page', 'Unbekannt')

        return f"\nGenerierte Frage (Quelle: {source_type}, {file_name}, Seite {page}):\n{question}"

    def generate_question(self, topic, question_type="mc"):
        """
        Generiert eine Frage zum angegebenen Thema
        question_type: 'mc' für Multiple Choice, 'sc' für Single Choice
        """
        try:
            # 1. Relevante Dokumente zum Thema finden
            relevant_docs = self.vectorstore.similarity_search(
                topic,
                k=2,
                filter={"source_type": "Hauptskript"}  # Bevorzuge Hauptskript für Fragen
            )

            if not relevant_docs:
                return {"error": "Ich konnte keine relevanten Informationen für eine Frage finden."}

            # 2. Prompt für Frage
            doc = relevant_docs[0]

            if question_type == "mc":
                prompt_type = "Multiple-Choice-Frage (mehrere Antworten können richtig sein)"
            else:
                prompt_type = "Single-Choice-Frage (nur eine Antwort ist richtig)"

            prompt = f"""
            Erstelle eine {prompt_type} zum Thema: {topic}
            Basierend auf diesem Kontext: {doc.page_content}

            Gib deine Antwort im folgenden JSON-Format zurück:
            {{
                "question": "Die Frage hier",
                "options": {{
                    "A": "Option A",
                    "B": "Option B",
                    "C": "Option C",
                    "D": "Option D"
                }},
                "correct_answers": ["A", "C"]  // Bei Single-Choice nur ein Element, z.B. ["B"]
            }}

            Die Frage sollte das Verständnis des Themas testen.
            """

            # 3. Frage generieren
            response = self.llm.invoke(prompt)

            # 4. Antwort parsen
            import json
            import re

            # Extrahiere JSON aus der Antwort
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return {"error": "Konnte keine gültige Frage generieren. Bitte versuchen Sie es erneut."}

            try:
                json_str = json_match.group(0)
                question_data = json.loads(json_str)
            except json.JSONDecodeError:
                return {"error": "Konnte das JSON-Format nicht korrekt parsen. Bitte versuchen Sie es erneut."}

            # Speichere die korrekten Antworten für spätere Überprüfung
            self.last_correct_answers = question_data["correct_answers"]

            # Formatiere die Rückgabe
            return {
                "question_text": question_data["question"],
                "options": question_data["options"],
                "source": {
                    "type": doc.metadata.get('source_type', 'Unbekannt'),
                    "file": doc.metadata.get('file_name', 'Unbekannt'),
                    "page": doc.metadata.get('page', 'Unbekannt')
                }
            }

        except Exception as e:
            return {"error": f"Fehler bei der Fragengenerierung: {str(e)}"}
