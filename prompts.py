def get_answer_prompt(language, question, documents):
    """
    Erstellt einen Prompt für die Beantwortung von Fragen basierend auf der erkannten Sprache
    """
    if language == 'de':
        prompt = f"""
        Du bist ein spezialisierter Tutor für das Fach "Business Software 2".

        AUFGABE:
        Beantworte die folgende Frage präzise und strukturiert, basierend ausschließlich auf den bereitgestellten Informationen.

        WICHTIGE REGELN:
        - Verwende NUR die unten angegebenen Informationen
        - Wenn die Informationen nicht ausreichen, sage ehrlich "Ich kann diese Frage mit den verfügbaren Informationen nicht vollständig beantworten"
        - Halte deine Antwort klar, prägnant und fachlich korrekt
        - Antworte auf Deutsch
        - Verwende keine Einleitungen wie "Basierend auf den Informationen..." oder "Laut den bereitgestellten Quellen..."

        FRAGE:
        {question}

        VERFÜGBARE INFORMATIONEN:
        """
    else:
        prompt = f"""
        You are a specialized tutor for the subject "Business Software 2".

        TASK:
        Answer the following question precisely and in a structured manner, based exclusively on the provided information.

        IMPORTANT RULES:
        - Use ONLY the information provided below
        - If the information is insufficient, honestly state "I cannot fully answer this question with the available information"
        - Keep your answer clear, concise, and technically accurate
        - Answer in English
        - Do not use introductions like "Based on the information..." or "According to the provided sources..."

        QUESTION:
        {question}

        AVAILABLE INFORMATION:
        """

    for i, doc in enumerate(documents):
        source_type = doc.metadata.get('source_type', 'Unknown' if language == 'en' else 'Unbekannt')
        file_name = doc.metadata.get('file_name', 'Unknown' if language == 'en' else 'Unbekannt')
        page = doc.metadata.get('page', 'Unknown' if language == 'en' else 'Unbekannt')

        if language == 'de':
            prompt += f"\n[{i+1}] Quelle: {source_type} ({file_name}, Seite {page+1})\n"
        else:
            prompt += f"\n[{i+1}] Source: {source_type} ({file_name}, Page {page+1})\n"

        prompt += f"{doc.page_content}\n"

    return prompt

def get_question_prompt(language, topic, question_type, context):
    """Liefert den Prompt für die Fragengenerierung in der angegebenen Sprache"""
    if language == "de":
        if question_type == "mc":
            return f"""
            Erstelle eine präzise Multiple-Choice-Frage zum Thema: {topic}

            WICHTIG:
            1. Verwende NUR Informationen aus dem bereitgestellten Kontext
            2. Die korrekten Antworten MÜSSEN direkt aus dem Kontext ableitbar sein
            3. Erstelle genau 4 Antwortoptionen (A-D)
            4. Es sollen mindestens 2 von 4 Antwortmöglichkeiten korrekt sein 
            5. Falsche Antworten müssen plausibel sein
            6. Verwende keine Optionen wie "Alle oben genannten" oder "Keine der genannten"
            7. Überprüfe jede Antwortoption gegen den Kontext auf Korrektheit
            8. Stelle sicher, dass die als korrekt markierten Antworten tatsächlich mit dem Kontext übereinstimmen
            9. Bei Multiple-Choice sollen nicht immer die gleichen Auswahloptionen (A, B, C oder D) korrekt sein und es können mehr als eine Antwort richtig sein

            KONTEXT:
            {context}

            ANTWORTFORMAT (strikt einhalten):
            {{
            "question": "Deine präzise Fachfrage hier",
            "options": {{
            "A": "Erste Option",
            "B": "Zweite Option",
            "C": "Dritte Option",
            "D": "Vierte Option"
            }},
            "correct_answers": ["X", "Y"]
            }}
            """
        else:
            return f"""
            Erstelle eine präzise Single-Choice-Frage zum Thema: {topic}

            WICHTIG:
            1. Verwende NUR Informationen aus dem bereitgestellten Kontext
            2. Die korrekten Antworten MÜSSEN direkt aus dem Kontext ableitbar sein
            3. Erstelle genau 4 Antwortoptionen (A-D)
            4. Nur EINE Antwort darf korrekt sein
            5. Falsche Antworten müssen plausibel sein
            6. Verwende keine Optionen wie "Alle oben genannten" oder "Keine der genannten"
            7. Überprüfe jede Antwortoption gegen den Kontext auf Korrektheit
            8. Stelle sicher, dass die als korrekt markierten Antworten tatsächlich mit dem Kontext übereinstimmen
            9. Bei Single-Choice sollte nicht immer die gleiche Auswahloption (A, B, C oder D) korrekt sein und genau eine der Antworten soll nur richtig sein

            KONTEXT:
            {context}

            ANTWORTFORMAT (strikt einhalten):
            {{
            "question": "Deine präzise Fachfrage hier",
            "options": {{
            "A": "Erste Option",
            "B": "Zweite Option",
            "C": "Dritte Option",
            "D": "Vierte Option"
            }},
            "correct_answers": ["X"]
            }}
            """
    else:  
        if question_type == "mc":
            return f"""
            Create a precise multiple-choice question about: {topic}

            IMPORTANT:
            1. Use ONLY information from the context provided
            2. The correct answers MUST be directly derivable from the context
            3. Create exactly 4 answer options (A-D)
            4. At least 2 out of 4 answers have to be correct
            5. Wrong answers must be plausible
            6. Do not use options such as "All of the above" or "None of the above"
            7. Check each answer option against the context for correctness
            8. Make sure that the answers marked as correct actually match the context
            9. With multiple choice, the same selection options (A, B, C or D) should not always be correct and more than one answer can be correct

            CONTEXT:
            {context}

            RESPONSE FORMAT (strictly adhere to):
            {{
            "question": "Your precise technical question here",
            "options": {{
            "A": "First option",
            "B": "Second option",
            "C": "Third option",
            "D": "Fourth option"
            }},
            "correct_answers": ["X", "Y"]
            }}
            """
        else: 
            return f"""
            Create a precise single-choice question about: {topic}

            IMPORTANT:
            1. Use ONLY information from the context provided
            2. The correct answer MUST be directly derivable from the context
            3. Create exactly 4 answer options (A-D)
            4. Only ONE answer must be correct
            5. Incorrect answers must be plausible
            6. Do not use options like "All of the above" or "None of the above"
            7. Check each answer option against the context for correctness
            8. Make sure that the answer marked as correct actually matches the context
            9. The correct answer should be random - NOT always B or always the same option

            CONTEXT:
            {context}

            RESPONSE FORMAT (strictly adhere to):
            {{
            "question": "Your precise technical question here",
            "options": {{
            "A": "First option",
            "B": "Second option",
            "C": "Third option",
            "D": "Fourth option"
            }},
            "correct_answers": ["X"]
            }}
            """

def get_topic_extraction_prompt(language, content):
    """Liefert den Prompt zur Extraktion eines Themas aus einem Dokument"""
    if language == "de":
        return f"""
        Hier hast du alle relevanten Informationen von genau dieser Folie:{content}
        Entscheide dich basierend auf nur diesen Informationen für ein passendes Thema für eine Prüfungsfrage
        Gib keine Erklärungen oder Einleitungen, sondern nur das Thema der Prüfungsfrage zurück.
        """
    else:
        return f"""
        Here you have all relevant information from a slide:

        {content}

        Create a suitable exam question with corresponding answer options based solely on this information.
        Use only the information from this slide.
        Do not provide explanations or introductions, only return the topic of the exam question.
        """

def get_question_variation_prompt(language, topic, previous_questions_text, context):
    """Liefert den Prompt zur Generierung einer Variation einer Frage"""
    if language == "de":
        return f"""
        Du bist ein Experte für Business Software und Prüfungsvorbereitung.
        Generiere eine VÖLLIG NEUE Prüfungsfrage zum Thema '{topic}', die sich von allen bisherigen Fragen deutlich unterscheidet.

        Basiere deine Frage auf folgendem Kontext aus dem Kursmaterial:
        '{context}'

        BEREITS GESTELLTE FRAGEN (NICHT WIEDERHOLEN):
        {previous_questions_text}

        Wichtig:
        - Erstelle eine Frage, die sich inhaltlich UND strukturell von den bisherigen unterscheidet
        - Fokussiere auf einen ANDEREN Aspekt oder Teilbereich des Themas
        - Verwende einen anderen Fragetyp (z.B. Anwendung, Definition, Vergleich)
        - Stelle sicher, dass die Frage einzigartig ist und nicht nur eine Umformulierung

        Wähle einen der folgenden Ansätze:
        - Praktische Anwendung statt Theorie
        - Spezifische Technologie oder Methode
        - Vor- oder Nachteile
        - Implementierungsherausforderungen
        - Historische Entwicklung
        - Vergleich mit alternativen Konzepten
        - Zukunftsperspektiven

        Formuliere eine präzise, prüfungsrelevante Frage ohne Einleitung oder Erklärung.
        Füge eine zufällige Zahl zwischen 1-1000 am Ende deiner Antwort hinzu, um Einzigartigkeit zu gewährleisten.
        """
    else:
        return f"""
        You are an expert in Business Software and exam preparation.
        Generate a COMPLETELY NEW exam question on the topic '{topic}' that differs significantly from all previous questions.

        Base your question on the following context from the course material:
        '{context}'

        PREVIOUSLY ASKED QUESTIONS (DO NOT REPEAT):
        {previous_questions_text}

        Important:
        - Create a question that differs in content AND structure from the previous ones
        - Focus on a DIFFERENT aspect or sub-area of the topic
        - Use a different question type (e.g., application, definition, comparison)
        - Ensure that the question is unique and not just a reformulation

        Choose one of the following approaches:
        - Practical application instead of theory
        - Specific technology or method
        - Advantages or disadvantages
        - Implementation challenges
        - Historical development
        - Comparison with alternative concepts
        - Future perspectives

        Formulate a precise, exam-relevant question without introduction or explanation.
        Add a random number between 1-1000 at the end of your answer to ensure uniqueness.
        """

def get_validation_prompt(language, doc_content, question, options, original_correct_answers):
    if language == "de":
        return f"""
        AUFGABE: Überprüfe die Korrektheit der Antworten für eine Multiple-Choice-Frage.

        ORIGINALTEXT:
        {doc_content}

        FRAGE:
        {question}

        ANTWORTOPTIONEN:
        A: {options['A']}
        B: {options['B']}
        C: {options['C']}
        D: {options['D']}

        ANGEGEBENE KORREKTE ANTWORTEN: {', '.join(original_correct_answers)}

        ANWEISUNGEN:
        1. Überprüfe SORGFÄLTIG, ob die angegebenen korrekten Antworten tatsächlich mit dem Originaltext übereinstimmen.
        2. Ignoriere dein eigenes Wissen und stütze dich NUR auf den Originaltext.
        3. Wenn die angegebenen korrekten Antworten NICHT mit dem Originaltext übereinstimmen, korrigiere sie.
        4. Gib die tatsächlich korrekten Antworten zurück.
        5. WICHTIG: Antworte NUR mit dem JSON-Format unten, ohne zusätzlichen Text.

        ANTWORTFORMAT (strikt einhalten):
        {{
        "correct_answers": ["X", "Y"],
        "explanation": "Kurze Erklärung, warum diese Antworten korrekt sind, mit Bezug auf den Originaltext."
        }}
        """
    else:
        return f"""
        TASK: Verify the correctness of answers for a multiple-choice question.

        ORIGINAL TEXT:
        {doc_content}

        QUESTION:
        {question}

        ANSWER OPTIONS:
        A: {options['A']}
        B: {options['B']}
        C: {options['C']}
        D: {options['D']}

        INDICATED CORRECT ANSWERS: {', '.join(original_correct_answers)}

        INSTRUCTIONS:
        1. CAREFULLY check if the indicated correct answers actually match the original text.
        2. Ignore your own knowledge and rely ONLY on the original text.
        3. If the indicated correct answers do NOT match the original text, correct them.
        4. Return the actually correct answers.
        5. IMPORTANT: Answer ONLY with the JSON format below, without additional text.

        RESPONSE FORMAT (strictly adhere to):
        {{
        "correct_answers": ["X", "Y"],
        "explanation": "Brief explanation of why these answers are correct, with reference to the original text."
        }}
        """