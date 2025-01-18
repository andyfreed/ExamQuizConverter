import re
import pandas as pd
from typing import Dict, List, Tuple

class ExamParser:
    def __init__(self):
        # Regex patterns for parsing
        self.question_pattern = r'(?:^\d+\.|^Q\d+\.|\n\d+\.|\nQ\d+\.)\s*(.*?)(?=(?:\n[A-D]\.|\n\d+\.|\nQ\d+\.|$))'
        self.answer_pattern = r'([A-D])\.\s*(.*?)(?=(?:\n[A-D]\.|\n\d+\.|\nQ\d+\.|$))'
        self.correct_answer_pattern = r'Correct Answer:\s*([A-D])'

    def parse_content(self, content: str) -> List[Dict]:
        """Parse the exam content into structured format."""
        # Split content into individual questions
        questions_raw = re.finditer(self.question_pattern, content, re.DOTALL)
        parsed_questions = []

        current_position = 0
        for q_match in questions_raw:
            question_text = q_match.group(1).strip()
            
            # Find the next question start or end of file
            next_q_start = len(content)
            next_matches = re.finditer(self.question_pattern, content)
            for m in next_matches:
                if m.start() > q_match.start():
                    next_q_start = m.start()
                    break
            
            # Extract the current question block
            question_block = content[q_match.start():next_q_start]
            
            # Find answers
            answers = {}
            for ans_match in re.finditer(self.answer_pattern, question_block, re.DOTALL):
                letter = ans_match.group(1)
                answer_text = ans_match.group(2).strip()
                answers[letter] = answer_text

            # Find correct answer
            correct_answer = None
            correct_match = re.search(self.correct_answer_pattern, question_block)
            if correct_match:
                correct_answer = correct_match.group(1)

            # Create question dictionary
            question_dict = {
                'Question': question_text,
                'A': answers.get('A', ''),
                'B': answers.get('B', ''),
                'C': answers.get('C', ''),
                'D': answers.get('D', ''),
                'Correct Answer': correct_answer or ''
            }
            parsed_questions.append(question_dict)

        return parsed_questions

    def create_dataframe(self, parsed_questions: List[Dict]) -> pd.DataFrame:
        """Convert parsed questions to pandas DataFrame."""
        return pd.DataFrame(parsed_questions)

    def process_file(self, content: str) -> pd.DataFrame:
        """Process file content and return DataFrame."""
        parsed_questions = self.parse_content(content)
        return self.create_dataframe(parsed_questions)
