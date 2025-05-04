import random
import json
import re
from utils import get_relevant_documents
from language_utils import get_error_message
from prompts import (
    get_question_prompt,
    get_topic_extraction_prompt,
    get_variation_instruction,
    get_validation_prompt,
    get_question_variation_prompt
)

class QuestionGenerator:
    def __init__(self, interface):
        self.interface = interface
        self.tutor = interface.tutor

    def generate_question_with_language(self, topic, question_type, previous_questions=None):
        """Generiert eine Frage in der ausgewählten Sprache"""

        if previous_questions is None:
            previous_questions = []

        try:
            docs = get_relevant_documents(
                self.tutor.vectorstore,
                topic,
                k=5,
                filter_type="Hauptskript"
            )

            if not docs:
                error_msg = get_error_message(self.interface.question_language, "no_documents")
                return {"error": error_msg}

            doc = random.choice(docs[:3]) if len(docs) >= 3 else docs[0]

            prompt = get_question_prompt(
                self.interface.question_language,
                topic,
                question_type,
                doc.page_content
            )

            response = self.tutor.llm.invoke(prompt)
            question_data = self._parse_question_response(response, doc)
            max_attempts = 3
            attempts = 0

            while attempts < max_attempts and not self.is_question_unique(question_data, previous_questions):
                if len(docs) > 1:
                    doc = random.choice([d for d in docs if d != doc])

                prompt = get_question_prompt(
                    self.interface.question_language,
                    topic,
                    question_type,
                    doc.page_content
                )

                response = self.tutor.llm.invoke(prompt)
                question_data = self._parse_question_response(response, doc)
                attempts += 1

            return question_data

        except Exception as e:
            error_msg = get_error_message(self.interface.question_language, "question_generation")
            return {"error": f"{error_msg}: {str(e)}"}

    def _parse_question_response(self, response, doc):
        """Parst die LLM-Antwort und extrahiert die Fragedaten mit Validierung"""
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            error_msg = get_error_message(self.interface.question_language, "invalid_question")
            return {"error": error_msg}

        try:
            json_str = json_match.group(0)
            question_data = json.loads(json_str)
            validated_data = self._validate_correct_answers(question_data, doc)

            self.tutor.last_correct_answers = validated_data["correct_answers"]

            return {
                "question_text": validated_data["question"],
                "options": validated_data["options"],
                "source": {
                    "type": doc.metadata.get('source_type', 'Unknown' if self.interface.question_language == "en" else "Unbekannt"),
                    "file": doc.metadata.get('file_name', 'Unknown' if self.interface.question_language == "en" else "Unbekannt"),
                    "page": doc.metadata.get('page', 'Unknown' if self.interface.question_language == "en" else "Unbekannt")
                }
            }
        except json.JSONDecodeError:
            error_msg = get_error_message(self.interface.question_language, "json_parse")
            return {"error": error_msg}

    def generate_random_question_internal(self, question_type):
        """Generiert eine Frage mit einem zufällig aus dem Vektorspeicher extrahierten Thema"""
        q_type_code = "mc" if "Multiple" in question_type else "sc"

        try:
            random_docs = self.get_random_documents(5)

            if not random_docs:
                error_msg = get_error_message(self.interface.question_language, "no_vectorstore_docs")
                return {"question_text": error_msg, "options": {}}

            random_doc = random.choice(random_docs)
            topic_prompt = get_topic_extraction_prompt(
                self.interface.question_language,
                random_doc.page_content
            )

            topic = self.tutor.llm.invoke(topic_prompt).strip()

            topic = topic.replace('"', '').replace("'", "").strip()
            if topic.lower().startswith("thema:"):
                topic = topic[6:].strip()
            if topic.lower().startswith("topic:"):
                topic = topic[6:].strip()

            print(f"Extrahiertes Thema: {topic}")

            prompt = get_question_prompt(
                self.interface.question_language,
                topic,
                q_type_code,
                random_doc.page_content
            )

            response = self.tutor.llm.invoke(prompt)
            question_data = self._parse_question_response(response, random_doc)

            if "error" in question_data:
                return {"question_text": question_data["error"], "options": {}}

            self.interface.current_question["options"] = question_data["options"]
            self.interface.current_question["correct_answers"] = self.tutor.last_correct_answers
            self.interface.current_question["question_type"] = q_type_code
            
            question_text = question_data['question_text']

            return {
                "question_text": question_text,
                "options": question_data["options"],
                "question_type": question_type
            }
        except Exception as e:
            error_msg = get_error_message(self.interface.question_language, "question_generation")
            return {"question_text": f"{error_msg}: {str(e)}", "options": {}}

    def _extract_json_from_response(self, response):
        """Extrahiert JSON aus der LLM-Antwort mit robusteren Methoden"""
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
    
        lines = response.split('\n')
        json_lines = []
        in_json = False

        for line in lines:
            line = line.strip()
            if line.startswith('{') and not in_json:
                in_json = True
                json_lines.append(line)
            elif in_json:
                json_lines.append(line)
                if line.endswith('}'):
                    in_json = False
                    break
                
        if json_lines:
            try:
                return json.loads(''.join(json_lines))
            except json.JSONDecodeError:
                pass
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        return None

    def _validate_correct_answers(self, question_data, doc):
        """Validiert die korrekten Antworten gegen den Originaltext mit verbesserter Robustheit"""
        question = question_data["question"]
        options = question_data["options"]
        original_correct_answers = question_data["correct_answers"]
        validation_prompt = get_validation_prompt(
            self.interface.question_language,
            doc.page_content,
            question,
            options,
            original_correct_answers
        )

        validation_response = self.tutor.llm.invoke(validation_prompt)
        validation_data = self._extract_json_from_response(validation_response)

        if not validation_data:
            print("Validierung fehlgeschlagen: Konnte kein gültiges JSON extrahieren")
            print(f"Antwort des LLM: {validation_response[:200]}...")
            return question_data

        try:
            validated_correct_answers = validation_data.get("correct_answers", original_correct_answers)
            valid_options = set("ABCD")
            validated_correct_answers = [ans for ans in validated_correct_answers if ans in valid_options]

            if not validated_correct_answers:
                print("Validierung ergab keine gültigen Antworten, behalte ursprüngliche")
                return question_data
            
            if set(validated_correct_answers) != set(original_correct_answers):
                print(f"Korrektur der Antworten: {original_correct_answers} -> {validated_correct_answers}")
                print(f"Erklärung: {validation_data.get('explanation', 'Keine Erklärung verfügbar')}")

            question_data["correct_answers"] = validated_correct_answers

            return question_data
        except Exception as e:
            print(f"Fehler bei der Validierung: {e}")
            return question_data

    def get_random_documents(self, count):
        """Holt wirklich zufällige Dokumente aus dem Vektorspeicher ohne vordefinierte Themen"""
        try:
            try:
                all_docs = list(self.tutor.vectorstore._collection.get(
                    where={"source_type": "Hauptskript"},
                    limit=150
                ))
                if len(all_docs) >= 10:
                    print(f"Methode 1: {len(all_docs)} Dokumente gefunden")
                    return random.sample(all_docs, min(count, len(all_docs)))
            except Exception as collection_error:
                print(f"Methode 1 fehlgeschlagen: {collection_error}")
                pass

            all_docs = self.tutor.vectorstore.similarity_search(
                "",
                k=150,
                filter={"source_type": "Hauptskript"}
            )
            print(f"Fallback-Methode: {len(all_docs)} Dokumente gefunden")

            if len(all_docs) < 10:
                all_docs = self.tutor.vectorstore.similarity_search(
                    "",
                    k=150
                )
                print(f"Fallback ohne Filter: {len(all_docs)} Dokumente gefunden")

            if len(all_docs) <= count:
                return all_docs
            return random.sample(all_docs, count)
        except Exception as e:
            print(f"Fehler beim Abrufen zufälliger Dokumente: {e}")
            return []

    def is_question_unique(self, new_question, previous_questions, threshold=0.7):
        """Überprüft, ob eine Frage ausreichend einzigartig ist im Vergleich zu vorherigen Fragen"""
        if not previous_questions:
            return True

        from difflib import SequenceMatcher

        if "question_text" in new_question and "\n\n" in new_question["question_text"]:
            new_question_text = new_question["question_text"].split("\n\n", 1)[1]
        else:
            new_question_text = new_question.get("question_text", "")

        for prev_q in previous_questions:
            prev_text = prev_q.get("question_text", "")
            if "\n\n" in prev_text:
                prev_text = prev_text.split("\n\n", 1)[1]

            similarity = SequenceMatcher(None, new_question_text, prev_text).ratio()
            if similarity > threshold:
                print(f"Frage zu ähnlich (Ähnlichkeit: {similarity:.2f})")
                return False

        return True

    def generate_question_variation(self, topic, question_type, previous_questions):
        """Generiert eine Variation einer Frage zu einem bestimmten Thema"""
        try:
            docs = get_relevant_documents(
                self.tutor.vectorstore,
                topic,
                k=5,
                filter_type="Hauptskript"
            )

            if docs:
                random_doc = random.choice(docs)
                context = random_doc.page_content
            else:
                context = "Keine spezifischen Informationen verfügbar."

            previous_questions_text = "\n".join([f"- {q['question_text']}" for q in previous_questions])

            variation_prompt = get_question_variation_prompt(
                self.interface.question_language,
                topic,
                previous_questions_text,
                context
            )

            subtopic = self.tutor.llm.invoke(variation_prompt).strip()
            subtopic = subtopic.replace('"', '').replace("'", "").strip()
            return f"{topic} - {subtopic}"
        except Exception as e:
            print(f"Fehler bei der Unterthema-Generierung: {e}")
            return f"{topic} (Variation {len(previous_questions) + 1})"