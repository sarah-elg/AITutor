import random
import json
import re

class QuestionGenerator:
    def __init__(self, interface):
        self.interface = interface
        self.tutor = interface.tutor

    def generate_question_with_language(self, topic, question_type):
        """Generiert eine Frage in der ausgewählten Sprache"""
        if self.interface.question_language == "en":
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
            return self.tutor.generate_question(topic, question_type, "de")

    def generate_random_question_internal(self, question_type):
        """Generiert eine Frage mit einem zufällig aus dem Vektorspeicher extrahierten Thema"""
        q_type_code = "mc" if "Multiple" in question_type else "sc"

        try:
            # 1. Hole zufällige Dokumente aus dem Vektorspeicher
            random_docs = self.get_random_documents(1)  # Hole ein zufälliges Dokument

            if not random_docs:
                error_msg = "Keine Dokumente im Vektorspeicher gefunden" if self.interface.question_language == "de" else "No documents found in vector store"
                return {"question_text": error_msg, "options": {}}

            random_doc = random_docs[0]

            # 2. Extrahiere ein Schlüsselthema aus dem Dokument
            topic = self.extract_key_topic(random_doc.page_content)

            print(f"Extrahiertes Thema: {topic}")

            # 3. Generiere Frage mit dem extrahierten Thema
            question_data = self.generate_question_with_language(topic, q_type_code)

            if "error" in question_data:
                return {"question_text": question_data["error"], "options": {}}

            self.interface.current_question["options"] = question_data["options"]
            self.interface.current_question["correct_answers"] = self.tutor.last_correct_answers
            self.interface.current_question["question_type"] = q_type_code

            # Füge das Thema zur Frage hinzu, damit der Benutzer weiß, worum es geht
            question_text = f"Thema: {topic}\n\n{question_data['question_text']}"

            return {
                "question_text": question_text,
                "options": question_data["options"],
                "question_type": question_type
            }
        except Exception as e:
            error_msg = "Fehler bei der Fragen-Generierung" if self.interface.question_language == "de" else "Error generating question"
            return {"question_text": f"{error_msg}: {str(e)}", "options": {}}

    def get_random_documents(self, count=3):
        """Holt wirklich zufällige Dokumente aus dem Vektorspeicher ohne vordefinierte Themen"""
        try:
            # 1. Hole alle verfügbaren Dokumente aus dem Hauptskript
            # Wir verwenden eine sehr allgemeine Abfrage, um möglichst viele Dokumente zu erhalten
            all_docs = self.tutor.vectorstore.similarity_search(
                "Business Software",  # Sehr allgemeine Abfrage
                k=50,  # Hole eine größere Anzahl von Dokumenten
                filter={"source_type": "Hauptskript"}
            )

            # 2. Falls nicht genug Dokumente gefunden wurden, versuche es ohne Filter
            if len(all_docs) < 10:
                all_docs = self.tutor.vectorstore.similarity_search(
                    "Business Software",
                    k=50
                )

            # 3. Wähle zufällig aus den gefundenen Dokumenten aus
            if len(all_docs) <= count:
                return all_docs
            return random.sample(all_docs, count)
        except Exception as e:
            print(f"Fehler beim Abrufen zufälliger Dokumente: {e}")
            return []

    def extract_key_topic(self, text):
        """Extrahiert ein Schlüsselthema aus dem Text ohne Vorgaben"""
        # Verwende das LLM, um ein relevantes Thema zu extrahieren
        prompt = f"""
        Du bist ein Experte für Business Software 2.
        Extrahiere ein einzelnes, präzises Fachthema aus dem folgenden Text, das sich für eine Prüfungsfrage eignet.
        Das Thema sollte spezifisch genug sein, um eine fokussierte Frage zu ermöglichen.
        Gib nur das Thema zurück, ohne zusätzlichen Text oder Erklärungen.

        Text: {text[:800]}
        """

        try:
            topic = self.tutor.llm.invoke(prompt).strip()
            # Entferne Anführungszeichen und andere Formatierungen
            topic = topic.replace('"', '').replace("'", "").strip()
            # Begrenze die Länge
            if len(topic) > 50:
                topic = topic[:50]
            return topic
        except Exception as e:
            print(f"Fehler bei der Themenextraktion: {e}")
            # Absoluter Notfall-Fallback
            return "Business Software"