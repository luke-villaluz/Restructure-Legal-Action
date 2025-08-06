"""Configuration settings for the legal contract analysis system."""

import os
from dotenv import load_dotenv

load_dotenv()

# Core Configuration
PROCESSING_PATH = os.getenv('PROCESSING_PATH')
SUMMARY_PATH = os.getenv('SUMMARY_PATH', 'data/summaries')
PROMPT_FILE = os.getenv('PROMPT_FILE', 'prompts/vendor_prompt.py')
SEARCH_TERMS = [term.strip() for term in os.getenv('SEARCH_TERMS', '').split(',') if term.strip()]
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# AI Provider Configuration
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL_NAME', 'llama2:3.1b')
PERPLEXITY_MODEL = os.getenv('PERPLEXITY_MODEL', 'sonar-pro')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
PERPLEXITY_BASE_URL = os.getenv('PERPLEXITY_BASE_URL', 'https://api.perplexity.ai')

# OCR Configuration
TESSERACT_PATH = os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')

# Testing Configuration
TEST_FOLDER = os.getenv('TEST_FOLDER')
