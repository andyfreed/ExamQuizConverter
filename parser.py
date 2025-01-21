import re
import pandas as pd
from typing import Dict, List, Tuple

class ExamParser:
    def __init__(self):
        # Pattern to identify complete questions with their answers - made more flexible
        self.question_block_pattern = r'(?:^|\n)\s*(\d+)\.\s*([^\n]+(?:\n(?!\d+\.|[A-Da-d]\.)[^\n]+)*)\s*(?:\n([A-Da-d]\..*?(?=\n\d+\.|\Z)))*'
        # Pattern for answer choices - more lenient with whitespace and empty answers
        self.answer_pattern = r'([A-Da-d])\.\s*(\*)?([^\n]*?)(\*)?(?=\n[A-Da-d]\.|\n\d+\.|\Z|\n\s*$)'
        # Pattern for answer key entries - more flexible format
        self.answer_key_pattern = r'(?:^|\n)\s*(\d+)\.\s*([A-Da-d])[.\s]*(?:\n|$)'

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
        # Print debug information
        print(f"Content length: {len(content)}")
        content = content.replace('\r\n', '\n').replace('\r', '\n').strip()

        # Parse answer key if provided
        answer_key = self.parse_answer_key(answer_key_content) if answer_key_content else {}

        # Split content into questions
        questions_raw = re.split(r'\n(?=\d+\.)', content)
        parsed_questions = []

        for raw_question in questions_raw:
            try:
                # Match question number and text
                question_match = re.match(r'\s*(\d+)\.\s*(.*?)(?=\n[A-Da-d]\.|\Z)', raw_question, re.DOTALL)
                if not question_match:
                    continue

                question_num = question_match.group(1)
                question_text = question_match.group(2).strip()

                # Skip if it looks like a year
                if question_text.strip().endswith('.') and question_text.strip()[:-1].isdigit():
                    continue

                # Clean the question text
                cleaned_question = self.clean_question_text(question_text)

                # Find answer choices
                answers = {'A': '', 'B': '', 'C': '', 'D': ''}
                correct_answer_text = ''

                answer_section = raw_question[question_match.end():]
                answer_matches = re.finditer(self.answer_pattern, answer_section, re.MULTILINE | re.DOTALL)

                for ans_match in answer_matches:
                    letter, start_asterisk, text, end_asterisk = ans_match.groups()
                    letter = letter.upper()
                    text = text.strip().strip('"')

                    # Store the answer text
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
                print(f"Error parsing question: {str(e)}")
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