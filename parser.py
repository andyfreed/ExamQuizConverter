import re
import pandas as pd
from typing import Dict, List, Tuple

class ExamParser:
    def __init__(self):
        # Pattern to split content into questions using question numbers
        self.split_pattern = r'(?=(?:^|\n)\d+\.)'
        # Pattern to extract question text and number
        self.question_pattern = r'(\d+)\.\s*([^\n]+)'
        # Pattern to extract answers with asterisk marker (at start or end)
        self.answer_pattern = r'\n([A-D])\.\s*(\*)?([^\n]+?)(?:\s*\*)?(?=\n|$)'

    def parse_content(self, content: str) -> List[Dict]:
        """Parse the exam content into structured format."""
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # Split content into questions using question numbers
        questions_blocks = re.split(self.split_pattern, content.strip())
        parsed_questions = []

        for block in questions_blocks:
            if not block.strip():
                continue

            # Find question number and text
            question_match = re.search(self.question_pattern, block)
            if not question_match:
                continue

            question_num, question_text = question_match.groups()

            # Find answers and check for asterisk
            answers = {
                'A': '',
                'B': '',
                'C': '',
                'D': ''
            }
            correct_answer_text = ''

            # Look for answers with potential asterisk at start or end
            answer_matches = list(re.finditer(self.answer_pattern, block))
            for ans_match in answer_matches:
                letter, start_asterisk, text = ans_match.groups()
                # Check if this answer has an asterisk at start or end
                if start_asterisk or '*' in text:
                    correct_answer_text = text.replace('*', '').strip()
                    text = text.replace('*', '').strip()
                answers[letter] = text.strip()

            # Only add if we have both question and at least one answer
            if question_text and any(answers.values()):
                question_dict = {
                    'Question': f"{question_num}. {question_text.strip()}",
                    'answer choice A': answers['A'],
                    'answer choice B': answers['B'],
                    'answer choice C': answers['C'],
                    'answer choice D': answers['D'],
                    'Correct Answer': correct_answer_text
                }
                parsed_questions.append(question_dict)

        return parsed_questions

    def create_dataframe(self, parsed_questions: List[Dict]) -> pd.DataFrame:
        """Convert parsed questions to pandas DataFrame."""
        if not parsed_questions:
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['Question', 'answer choice A', 'answer choice B', 
                                      'answer choice C', 'answer choice D', 'Correct Answer'])
        return pd.DataFrame(parsed_questions)

    def process_file(self, content: str) -> pd.DataFrame:
        """Process file content and return DataFrame."""
        parsed_questions = self.parse_content(content)
        return self.create_dataframe(parsed_questions)