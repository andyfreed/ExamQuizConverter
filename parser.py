import re
import pandas as pd
from typing import Dict, List, Tuple

class ExamParser:
    def __init__(self):
        # Updated regex patterns for more flexible parsing
        self.question_pattern = r'(?:^|\n)(?:\d+\.|Q\d+\.)\s*([^\n]+(?:\n(?![A-D]\.|\d+\.|Q\d+\.|Correct)[^\n]+)*)'
        self.answer_pattern = r'\n([A-D])\.\s*([^\n]+(?:\n(?![A-D]\.|\d+\.|Q\d+\.|Correct)[^\n]+)*)'
        self.correct_answer_pattern = r'(?:\n|\s)Correct Answer:\s*([A-D])'

    def parse_content(self, content: str) -> List[Dict]:
        """Parse the exam content into structured format."""
        # Add newline at start and end for consistent matching
        content = f"\n{content}\n"

        # Split content into individual questions
        questions_raw = re.finditer(self.question_pattern, content, re.MULTILINE)
        parsed_questions = []

        for q_match in questions_raw:
            question_start = q_match.start()
            question_text = q_match.group(1).strip()

            # Find the next question start or end of file
            next_q_start = len(content)
            for m in re.finditer(self.question_pattern, content):
                if m.start() > question_start:
                    next_q_start = m.start()
                    break

            # Extract the current question block
            question_block = content[question_start:next_q_start]

            # Initialize answers dictionary
            answers = {
                'A': '',
                'B': '',
                'C': '',
                'D': ''
            }

            # Find answers
            answer_matches = re.finditer(self.answer_pattern, question_block)
            for ans_match in answer_matches:
                letter = ans_match.group(1)
                answer_text = ans_match.group(2).strip()
                if letter in answers:
                    answers[letter] = answer_text

            # Find correct answer
            correct_answer = ''
            correct_match = re.search(self.correct_answer_pattern, question_block)
            if correct_match:
                correct_answer = correct_match.group(1)

            # Only add if we have a valid question
            if question_text and any(answers.values()):
                question_dict = {
                    'Question': question_text,
                    'A': answers['A'],
                    'B': answers['B'],
                    'C': answers['C'],
                    'D': answers['D'],
                    'Correct Answer': correct_answer
                }
                parsed_questions.append(question_dict)

        return parsed_questions

    def create_dataframe(self, parsed_questions: List[Dict]) -> pd.DataFrame:
        """Convert parsed questions to pandas DataFrame."""
        if not parsed_questions:
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['Question', 'A', 'B', 'C', 'D', 'Correct Answer'])
        return pd.DataFrame(parsed_questions)

    def process_file(self, content: str) -> pd.DataFrame:
        """Process file content and return DataFrame."""
        parsed_questions = self.parse_content(content)
        return self.create_dataframe(parsed_questions)