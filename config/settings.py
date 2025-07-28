import os
from dotenv import load_dotenv

load_dotenv()

# Simple configuration
INPUT_DIRECTORY = os.getenv('INPUT_DIRECTORY_PATH')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL_NAME', 'llama2:3.1b')
SEARCH_TERMS = [term.strip() for term in os.getenv('SEARCH_TERMS', '').split(',') if term.strip()]
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
OUTPUT_DIR = 'data/summaries'
TEST_FOLDER = os.getenv('TEST_FOLDER')
MAIN_TEST_FOLDER_PATH = os.getenv('MAIN_TEST_FOLDER_PATH')
