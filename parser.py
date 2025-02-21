import re
import pandas as pd
from typing import Dict, List, Tuple

class ExamParser:
    def __init__(self):
        # Updated pattern to handle company names with Inc., Ltd., etc.
        self.question_pattern = r'(\d+)\.\s*(.*?)(?=\s*(?:\n[A-Da-d]\.|$))'
        # Modified answer pattern to be more strict about answer format
        self.answer_pattern = r'(?:^|\n)\s*([A-Da-d])\.\s*(.*?)(?=\s*(?:\n[A-Da-d]\.|$|\n\d+\.|$))'
        # Answer key pattern
        self.answer_key_pattern = r'(?:^|\n)\s*(\d+)\.\s*([A-Da-d])[.\s]*(?:\n|$)'

    def parse_answer_key(self, answer_key_content: str) -> Dict[str, str]:
        """Parse answer key content into a dictionary."""
        if not answer_key_content:
            return {}

        answers = {}

        # More flexible pattern to match answer keys
        patterns = [
            r'(?:^|\n)\s*(\d+)\.\s*([A-Da-d])[.\s]*(?:\n|$)',  # Basic format: "1. A"
            r'(?:^|\n)\s*(\d+)[.\s]*([A-Da-d])[.\s]*(?:\n|$)',  # Alternative: "1 A"
            r'(?:^|\n)\s*(\d+)[)\s.]*([A-Da-d])[.\s]*(?:\n|$)',  # Format with parenthesis: "1) A"
            r'Question\s*(\d+)[:\s]*([A-Da-d])[.\s]*(?:\n|$)',   # Format with "Question": "Question 1: A"
        ]

        # Try each pattern
        for pattern in patterns:
            matches = re.finditer(pattern, answer_key_content, re.MULTILINE)
            for match in matches:
                question_num, answer_letter = match.groups()
                # Clean up and store the answer
                answers[question_num.strip()] = answer_letter.strip().upper()

        # If no matches found, try looking for answer key in a different format
        if not answers:
            # Look for answers in text like "The answer to question 1 is A"
            text_pattern = r'(?:answer|solution)(?:\s+to)?(?:\s+question)?\s*(\d+)(?:\s+is)?\s+([A-Da-d])'
            matches = re.finditer(text_pattern, answer_key_content.lower(), re.IGNORECASE)
            for match in matches:
                question_num, answer_letter = match.groups()
                answers[question_num.strip()] = answer_letter.strip().upper()

        return answers

    def parse_content(self, content: str, answer_key_content: str = None) -> List[Dict]:
        """Parse exam content into structured format."""
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        parsed_questions = []

        # Parse answer key if provided
        answer_key = self.parse_answer_key(answer_key_content) if answer_key_content else {}

        # Split content into question blocks more accurately
        questions_raw = re.split(r'\n(?=\d+\.)', content)

        for question_block in questions_raw:
            try:
                # Skip empty blocks
                if not question_block.strip():
                    continue

                # Match question with improved pattern
                question_match = re.match(self.question_pattern, question_block, re.DOTALL | re.MULTILINE)
                if not question_match:
                    continue

                question_num = question_match.group(1)
                question_text = question_match.group(2).strip().strip('"')

                # Skip if it's just a year
                if question_text.isdigit():
                    continue

                # Initialize answers with empty strings
                answers = {'A': '', 'B': '', 'C': '', 'D': ''}
                correct_answer_text = ''

                # Get the answer section after the question
                answer_section = question_block[len(question_match.group(0)):].strip()

                # Find all answer choices with improved pattern
                answer_matches = list(re.finditer(self.answer_pattern, '\n' + answer_section, re.DOTALL | re.MULTILINE))

                # Process each answer choice
                for match in answer_matches:
                    letter, text = match.groups()
                    letter = letter.upper()

                    # Clean and store the answer text
                    text = text.strip().strip('"').strip()
                    if text:  # Only store non-empty answers
                        answers[letter] = text

                        # Check for asterisk marking correct answer
                        if '*' in text:
                            correct_answer_text = text.replace('*', '').strip()
                            answers[letter] = correct_answer_text

                # Check answer key if no asterisk was found
                if not correct_answer_text and question_num in answer_key:
                    correct_letter = answer_key[question_num]
                    if correct_letter in answers:
                        correct_answer_text = answers[correct_letter]

                # Only add if we have a question
                if question_text:
                    question_dict = {
                        'Question': question_text,
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
            return pd.DataFrame(columns=['Question', 'answer choice A', 'answer choice B', 
                                          'answer choice C', 'answer choice D', 'Correct Answer'])
        return pd.DataFrame(parsed_questions)

    def process_file(self, content: str, answer_key_content: str = None) -> pd.DataFrame:
        """Process file content and return DataFrame."""
        parsed_questions = self.parse_content(content, answer_key_content)
        return self.create_dataframe(parsed_questions)