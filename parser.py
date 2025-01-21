import re
import pandas as pd
from typing import Dict, List, Tuple

class ExamParser:
    def __init__(self):
        # More flexible pattern to split content into questions
        self.split_pattern = r'\n*\s*(\d+)\.'
        # More flexible pattern to extract question text
        self.question_pattern = r'^\s*(\d+)\.\s*(.+?)(?=\n[A-D]\.|\Z)'
        # More flexible pattern for answers
        self.answer_pattern = r'([A-D])\.\s*(\*)?([^\n]+?)(?:\s*\*)?(?=\n[A-D]\.|\n\d+\.|\Z)'

    def parse_content(self, content: str) -> List[Dict]:
        """Parse the exam content into structured format."""
        # Normalize line endings and clean content
        content = content.replace('\r\n', '\n').replace('\r', '\n').strip()

        # Split content into questions
        questions_blocks = re.split(self.split_pattern, content)
        # Remove empty strings from the split
        questions_blocks = [block.strip() for block in questions_blocks if block.strip()]

        parsed_questions = []
        question_number = 1

        # Process pairs of question numbers and content
        for i in range(0, len(questions_blocks)-1, 2):
            try:
                question_num = questions_blocks[i]
                block = questions_blocks[i+1]

                # Extract question text using lookahead for answer choices
                full_text = f"{question_num}. {block}"
                question_match = re.search(self.question_pattern, full_text, re.DOTALL | re.MULTILINE)

                if not question_match:
                    print(f"Warning: Could not parse question {question_num}")
                    continue

                _, question_text = question_match.groups()

                # Initialize answers dictionary
                answers = {
                    'A': '',
                    'B': '',
                    'C': '',
                    'D': ''
                }
                correct_answer_text = ''

                # Find all answers in the block
                answer_matches = list(re.finditer(self.answer_pattern, block, re.MULTILINE | re.DOTALL))

                for ans_match in answer_matches:
                    letter, start_asterisk, text = ans_match.groups()
                    text = text.strip()

                    # Check for asterisk at start or end
                    if start_asterisk or '*' in text:
                        text = text.replace('*', '').strip()
                        correct_answer_text = text

                    answers[letter] = text

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

            except Exception as e:
                print(f"Error parsing question {question_number}: {str(e)}")

            question_number += 1

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