import re
import pandas as pd
from typing import Dict, List, Tuple

class ExamParser:
    def __init__(self):
        # Simple patterns that match common exam question formats
        self.question_pattern = r'(?:^|\n)(\d+)\.\s*([^\n]+)'
        self.answer_pattern = r'\n([A-D])\.\s*([^\n]+)'
        self.correct_answer_pattern = r'Correct Answer:\s*([A-D])'

    def parse_content(self, content: str) -> List[Dict]:
        """Parse the exam content into structured format."""
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # Split content into questions
        questions_blocks = re.split(r'\n\s*\n', content)
        parsed_questions = []

        for block in questions_blocks:
            if not block.strip():
                continue

            # Find question number and text
            question_match = re.search(self.question_pattern, block)
            if not question_match:
                continue

            question_num, question_text = question_match.groups()

            # Find answers
            answers = {
                'A': '',
                'B': '',
                'C': '',
                'D': ''
            }

            answer_matches = re.finditer(self.answer_pattern, block)
            for ans_match in answer_matches:
                letter, text = ans_match.groups()
                answers[letter] = text.strip()

            # Find correct answer
            correct_answer = ''
            correct_match = re.search(self.correct_answer_pattern, block)
            if correct_match:
                correct_answer = correct_match.group(1)

            # Only add if we have both question and at least one answer
            if question_text and any(answers.values()):
                question_dict = {
                    'Question': f"{question_num}. {question_text.strip()}",
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