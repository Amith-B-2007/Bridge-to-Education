import requests
import os
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3')

    def get_curriculum_prompt(self, grade, subject, language='en'):
        """Build curriculum-aware system prompt."""
        curriculum_map = {
            '1-5_Kannada': 'ಅಕ್ಷರಗಳು, ಮೂಲ ಸಂವಾದ, ಸರಳ ಶೈಲಿ',
            '1-5_English': 'Alphabets, Basic vocabulary, Simple sentences',
            '1-5_Maths': 'Numbers 1-100, Basic addition/subtraction, Shapes',
            '6-8_Maths': 'Algebra basics, Geometry, Fractions, Decimals',
            '9-10_Maths': 'Quadratic equations, Trigonometry, Calculus basics',
            '6-8_Science': 'Physics, Chemistry, Biology fundamentals',
            '9-10_Science': 'Advanced Physics, Organic Chemistry, Human Biology',
        }
        
        grade_range = f'1-5' if grade <= 5 else ('6-8' if grade <= 8 else '9-10')
        key = f'{grade_range}_{subject}'
        curriculum = curriculum_map.get(key, '')
        
        if language == 'kn':
            return f"""ನೀವು ಕನ್ನಡ ರಾಜ್ಯ ಶಾಲಾ ಪರಿಷದ್ ಪಠ್ಯಕ್ರಮದ ಪ್ರಕಾರ {grade}ನೇ ತರಗತಿಯ {subject} ವಿಷಯದ ಅರ್ಹ ಶಿಕ್ಷಕ.
ಚೆವುಕನ್ನಡದಲ್ಲಿ ಸಮಾಧಾನ ನೀಡಿ.
ಪಾಠ್ಯಕ್ರಮ: {curriculum}
ಉತ್ತರಗಳು ಸ್ಪಷ್ಟ ಮತ್ತು ಮಾನ್ಯವಾಗಿರಬೇಕು."""
        else:
            return f"""You are a Karnataka State Board certified teacher for grade {grade} {subject}.
Provide clear, step-by-step explanations aligned with the state curriculum.
Curriculum: {curriculum}
Always use examples from the Karnataka NCERT books."""

    def query(self, messages, grade, subject, language='en', stream=False):
        """Query Ollama API with curriculum context."""
        system_prompt = self.get_curriculum_prompt(grade, subject, language)
        
        formatted_messages = [
            {'role': 'system', 'content': system_prompt}
        ]
        formatted_messages.extend(messages)
        
        payload = {
            'model': self.model,
            'messages': formatted_messages,
            'stream': stream
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/api/chat',
                json=payload,
                stream=stream,
                timeout=30
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f'Ollama API error: {str(e)}')
            raise

    def is_available(self):
        """Check if Ollama service is running."""
        try:
            response = requests.get(f'{self.base_url}/api/tags', timeout=2)
            return response.status_code == 200
        except:
            return False
