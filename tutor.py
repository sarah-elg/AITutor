
from langchain_ollama import OllamaLLM

class OptimizedBS2Tutor:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = OllamaLLM(model="llama3.2", temperature=0.0)
        self.last_correct_answers = []  # Für die Fragen-Generierung
        self.language = language

# Übersetzungen für verschiedene Texte
    TRANSLATIONS = {
        "de": {
            "answer_prefix": "Antwort: ",
            "sources_label": "Quellen",
            "main_script": "Hauptskript",
            "all_sources": "Alle Quellen",
            "unknown": "Unbekannt",
            "page": "Seite",
            "error_processing": "Fehler bei der Verarbeitung der Frage: {}",
            "insufficient_info": "Ich konnte keine ausreichenden Informationen finden, um diese Frage zu beantworten."
        },
        "en": {
            "answer_prefix": "Answer: ",
            "sources_label": "Sources",
            "main_script": "Main Script",
            "all_sources": "All Sources",
            "unknown": "Unknown",
            "page": "Page",
            "error_processing": "Error processing question: {}",
            "insufficient_info": "I couldn't find sufficient information to answer this question."
        }
    }

def detect_language(self, text):
        """Erkennt die Sprache des Textes (vereinfachte Version)"""
        # Einfache Erkennung basierend auf häufigen deutschen Wörtern
        german_words = ["der", "die", "das", "und", "ist", "in", "zu", "den", "für", "auf", "mit", "dem", "nicht", "ein", "eine", "wie", "im", "von", "ich", "du", "er", "sie", "es", "wir", "ihr", "sie", "mein", "dein", "sein", "ihr", "unser", "euer", "ihr"]

        text_lower = text.lower()
        words = text_lower.split()

        # Zähle deutsche Wörter
        german_count = sum(1 for word in words if word in german_words)

        # Wenn mehr als 15% der Wörter deutsch sind, nehme Deutsch an
        if german_count / max(len(words), 1) > 0.15:
            return "de"
        else:
            return "en"

def ask_question(self, question, k=5, use_main_script_first=True):
        """
        Beantwortet eine Frage basierend auf dem Hauptskript und der Literatur
        """
        # Erkenne die Sprache der Frage
        language = self.detect_language(question)

        print(f"Erkannte Sprache: {language}")
        print(self.TRANSLATIONS[language]["processing_question"])

        try:
            # 1. Suche zuerst im Hauptskript, wenn gewünscht
            if use_main_script_first:
                # Suche mit Metadaten-Filter für Hauptskript
                main_docs = self.vectorstore.similarity_search(
                    question,
                    k=k,
                    filter={"source_type": "Hauptskript"}
                )
                print(self.TRANSLATIONS[language]["found_docs_main"].format(len(main_docs)))

                # Wenn genügend relevante Dokumente im Hauptskript gefunden wurden
                if len(main_docs) >= 2:
                    print(self.TRANSLATIONS[language]["generating_answer_main"])
                    answer = self._generate_answer(question, main_docs)
                    print(self.TRANSLATIONS[language]["answer_generated"])

                    # Prüfe, ob die Antwort ausreichend ist
                    if not self._is_insufficient_answer(answer):
                        return self._format_response(answer, main_docs, self.TRANSLATIONS[language]["main_script"], language)

            # 2. Suche in allen Dokumenten (Hauptskript + Literatur)
            print(self.TRANSLATIONS[language]["searching_all_docs"])
            all_docs = self.vectorstore.similarity_search(question, k=k)
            print(self.TRANSLATIONS[language]["found_docs_all"].format(len(all_docs)))

            print(self.TRANSLATIONS[language]["generating_answer_all"])
            answer = self._generate_answer(question, all_docs, language)
            print(self.TRANSLATIONS[language]["answer_generated"])

            return self._format_response(answer, all_docs, self.TRANSLATIONS[language]["all_sources"], language)

        except Exception as e:
            return self.TRANSLATIONS[language]["error_processing"].format(e)

def _is_insufficient_answer(self, answer):
        """Prüft, ob eine Antwort unzureichend ist"""
        insufficient_phrases = [
            "keine ausreichenden informationen",
            "nicht genügend informationen",
            "keine informationen",
            "nicht genug kontext",
            "kann ich nicht beantworten",
            "nicht in den bereitgestellten informationen"
            "no sufficient information",
            "not enough information",
            "no information",
            "not enough context",
            "cannot answer",
            "not in the provided information"
        ]

        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in insufficient_phrases)

def _generate_answer(self, question, documents, language):
        """Generiert eine Antwort basierend auf den relevanten Dokumenten"""
        # Wähle den richtigen Prompt basierend auf der Sprache
        if language == "de":
            prompt = f"""
            Du bist ein hilfreicher BS2-Tutor für das Fach "Business Software 2".
            Beantworte die folgende Frage basierend auf den gegebenen Informationen.
            Verwende nur die bereitgestellten Informationen. Wenn du die Antwort nicht in den
            Informationen findest, sage das ehrlich.
            Antworte auf Deutsch.

            Frage: {question}

            Relevante Informationen:
        """
        else:  # Englisch
            prompt = f"""
            You are a helpful BS2 tutor for the subject "Business Software 2".
            Answer the following question based on the given information.
            Use only the provided information. If you cannot find the answer in the
            information, please say so honestly.
            Answer in English.

            Question: {question}

            Relevant information:
            """

        for i, doc in enumerate(documents):
            source_type = doc.metadata.get('source_type', self.TRANSLATIONS[language]["unknown"])
            file_name = doc.metadata.get('file_name', self.TRANSLATIONS[language]["unknown"])
            page = doc.metadata.get('page', self.TRANSLATIONS[language]["unknown"])

            prompt += f"\n[{i+1}] {self.TRANSLATIONS[language]['sources_label']}: {source_type} ({file_name}, {self.TRANSLATIONS[language]['page']} {page+1})\n"
            prompt += f"{doc.page_content}\n"

        # Generiere Antwort
        answer = self.llm.invoke(prompt)
        return answer

def _format_response(self, answer, documents, source_label, language):
        """Formatiert die Antwort mit Quellenangaben"""
        response = f"\n{self.TRANSLATIONS[language]['answer_prefix']}{answer}\n\n{self.TRANSLATIONS[language]['sources_label']} ({source_label}):"

        for i, doc in enumerate(documents):
            source_type = doc.metadata.get('source_type', self.TRANSLATIONS[language]["unknown"])
            file_name = doc.metadata.get('file_name', self.TRANSLATIONS[language]["unknown"])
            page = doc.metadata.get('page', self.TRANSLATIONS[language]["unknown"])

            response += f"\n[{i+1}] {source_type}: {file_name}, {self.TRANSLATIONS[language]['page']} {page + 1}"

        return response

def generate_mc_question(self, topic):
        """Generiert eine Multiple-Choice-Frage zum angegebenen Thema"""
        try:
            # 1. Relevante Dokumente zum Thema finden
            relevant_docs = self.vectorstore.similarity_search(
                topic,
                k=2,
                filter={"source_type": "Hauptskript"}  # Bevorzuge Hauptskript für MC-Fragen
            )

            if not relevant_docs:
                return "Ich konnte keine relevanten Informationen für eine Frage finden." if language == "de" else "I couldn't find relevant information for a question."

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
            source_type = doc.metadata.get('source_type', self.TRANSLATIONS[language]["unknown"])
            file_name = doc.metadata.get('file_name', self.TRANSLATIONS[language]["unknown"])
            page = doc.metadata.get('page', self.TRANSLATIONS[language]["unknown"])

            if language == "de":
                return f"\nGenerierte Frage (Quelle: {source_type}, {file_name}, Seite {page}):\n{question}"
            else:
                return f"\nGenerated question (Source: {source_type}, {file_name}, Page {page}):\n{question}"

        except Exception as e:
            return f"Fehler bei der Fragengenerierung: {e}" if language == "de" else f"Error generating question: {e}"

def generate_question(self, topic, question_type="mc"):
        """
        Generiert eine Frage zum angegebenen Thema
        question_type: 'mc' für Multiple Choice, 'sc' für Single Choice
        """
        # Erkenne die Sprache des Themas
        language = self.detect_language(topic)

        try:
            # 1. Relevante Dokumente zum Thema finden
            relevant_docs = self.vectorstore.similarity_search(
                topic,
                k=2,
                filter={"source_type": "Hauptskript"}  # Bevorzuge Hauptskript für Fragen
            )

            if not relevant_docs:
                return {"error": "Ich konnte keine relevanten Informationen für eine Frage finden."} if language == "de" else "I couldn't find relevant information for a question."
                return {"error": error_msg}

            # 2. Prompt für Frage
            doc = relevant_docs[0]
        if language == "de":
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
        else:
            if question_type == "mc":
                    prompt_type = "multiple-choice question (multiple answers can be correct)"
            else:
                    prompt_type = "single-choice question (only one answer is correct)"

            prompt = f"""
                Create a {prompt_type} on the topic: {topic}
                Based on this context: {doc.page_content}

                Provide your answer in the following JSON format:
                {{
                    "question": "The question here",
                    "options": {{
                        "A": "Option A",
                        "B": "Option B",
                        "C": "Option C",
                        "D": "Option D"
                    }},
                    "correct_answers": ["A", "C"]  // For single-choice, only one element, e.g. ["B"]
                }}

                The question should test understanding of the topic.
                """

            # 3. Frage generieren
            response = self.llm.invoke(prompt)

            # 4. Antwort parsen
            import json
            import re

            # Extrahiere JSON aus der Antwort
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return {"error": "Konnte keine gültige Frage generieren. Bitte versuchen Sie es erneut."} if language == "de" else "Could not generate a valid question. Please try again."
    
            json_str = json_match.group(0)
            question_data = json.loads(json_str)

            # Speichere die korrekten Antworten für spätere Überprüfung
            self.last_correct_answers = question_data["correct_answers"]

            # Formatiere die Rückgabe
            return {
                "question_text": question_data["question"],
                "options": question_data["options"],
                "source": {
                    "type": doc.metadata.get('source_type', self.TRANSLATIONS[language]["unknown"]),
                    "file": doc.metadata.get('file_name', self.TRANSLATIONS[language]["unknown"]),
                    "page": doc.metadata.get('page', self.TRANSLATIONS[language]["unknown"])
                }
            }

        except Exception as e:
            error_msg = f"Fehler bei der Fragengenerierung: {str(e)}" if language == "de" else f"Error generating question: {str(e)}"
            return {"error": error_msg}
