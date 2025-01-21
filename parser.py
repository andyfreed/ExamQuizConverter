import re
import pandas as pd
from typing import Dict, List, Tuple

class ExamParser:
    def __init__(self):
        # Pattern to identify complete questions with their answers
        self.question_block_pattern = r'(?:^|\n)\s*(\d+)\.\s*([^\n]+(?:\n(?![A-Da-d]\.|\d+\.)[^\n]+)*)\s*(?:\n([A-Da-d]\..*?(?=\n\d+\.|\Z)))+' 
        # Pattern for answer choices with better asterisk handling
        self.answer_pattern = r'([A-Da-d])\.\s*(\*)?([^\n]+?)(\*)?(?=\n[A-Da-d]\.|\n\d+\.|\Z)'
        # Pattern for answer key entries
        self.answer_key_pattern = r'(?:^|\n)\s*(\d+)\.\s*([A-Da-d])\s*(?:\n|$)'

    def clean_question_text(self, question_text: str) -> str:
        """Remove question numbers and clean the text."""
        # Remove leading numbers and dots
        cleaned = re.sub(r'^\d+\.\s*', '', question_text)
        # Remove any years that might appear as numbers
        cleaned = re.sub(r'^\s*\d{4}\.\s*', '', cleaned)
        # Remove any remaining leading/trailing whitespace and quotes
        cleaned = cleaned.strip().strip('"')
        return cleaned

    def parse_answer_key(self, answer_key_content: str) -> Dict[str, str]:
        """Parse answer key content into a dictionary of question numbers and correct answer letters."""
        if not answer_key_content:
            return {}

        answers = {}
        matches = re.finditer(self.answer_key_pattern, answer_key_content, re.MULTILINE)
        for match in matches:
            question_num, answer_letter = match.groups()
            answers[question_num.strip()] = answer_letter.strip().upper()
        return answers

    def parse_content(self, content: str, answer_key_content: str = None) -> List[Dict]:
        """Parse the exam content into structured format."""
        # Normalize line endings and clean content
        content = content.replace('\r\n', '\n').replace('\r', '\n').strip()

        # Parse answer key if provided
        answer_key = self.parse_answer_key(answer_key_content) if answer_key_content else {}

        # Find all question blocks
        question_blocks = re.finditer(self.question_block_pattern, content, re.MULTILINE | re.DOTALL)
        parsed_questions = []

        for block in question_blocks:
            try:
                question_num = block.group(1)
                question_text = block.group(2).strip()
                answers_text = block.group(3)

                # Skip if it looks like a year or just a number
                if question_text.strip().endswith('.') and question_text.strip()[:-1].isdigit():
                    continue

                # Clean the question text
                cleaned_question = self.clean_question_text(question_text)

                # Initialize answers dictionary
                answers = {
                    'A': '',
                    'B': '',
                    'C': '',
                    'D': ''
                }
                correct_answer_text = ''

                # Find all answers in the answer text
                if answers_text:
                    answer_matches = re.finditer(self.answer_pattern, answers_text, re.MULTILINE | re.DOTALL)

                    for ans_match in answer_matches:
                        letter, start_asterisk, text, end_asterisk = ans_match.groups()
                        letter = letter.upper()
                        text = text.strip().strip('"')
                        answers[letter] = text

                        # Check for asterisk marking correct answer
                        if start_asterisk or end_asterisk or '*' in text:
                            text = text.replace('*', '').strip()
                            correct_answer_text = text
                            answers[letter] = text

                # Check answer key if no asterisk was found
                if not correct_answer_text and question_num in answer_key:
                    correct_letter = answer_key[question_num]
                    if correct_letter in answers:
                        correct_answer_text = answers[correct_letter]

                # Only add if we have both question and at least one answer
                if cleaned_question and any(answers.values()):
                    question_dict = {
                        'Question': cleaned_question,
                        'answer choice A': answers['A'],
                        'answer choice B': answers['B'],
                        'answer choice C': answers['C'],
                        'answer choice D': answers['D'],
                        'Correct Answer': correct_answer_text
                    }
                    parsed_questions.append(question_dict)

            except Exception as e:
                print(f"Error parsing question block: {str(e)}")
                continue

        return parsed_questions

    def create_dataframe(self, parsed_questions: List[Dict]) -> pd.DataFrame:
        """Convert parsed questions to pandas DataFrame."""
        if not parsed_questions:
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['Question', 'answer choice A', 'answer choice B', 
                                      'answer choice C', 'answer choice D', 'Correct Answer'])
        return pd.DataFrame(parsed_questions)

    def process_file(self, content: str, answer_key_content: str = None) -> pd.DataFrame:
        """Process file content and return DataFrame."""
        parsed_questions = self.parse_content(content, answer_key_content)
        return self.create_dataframe(parsed_questions)