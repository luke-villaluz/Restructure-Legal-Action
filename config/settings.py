import os
from dotenv import load_dotenv

load_dotenv()

# Simple configuration - use a different variable name to avoid conflicts
PROCESSING_PATH = os.getenv('PROCESSING_PATH')  # Changed from PATH to PROCESSING_PATH
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL_NAME', 'llama2:3.1b')
SEARCH_TERMS = [term.strip() for term in os.getenv('SEARCH_TERMS', '').split(',') if term.strip()]
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
OUTPUT_DIR = 'data/summaries'

# Perplexity Configuration
PERPLEXITY_MODEL = os.getenv('PERPLEXITY_MODEL', 'sonar-pro')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
PERPLEXITY_BASE_URL = os.getenv('PERPLEXITY_BASE_URL', 'https://api.perplexity.ai')

# OCR Configuration
ENABLE_OCR = os.getenv('ENABLE_OCR', 'true').lower() == 'true'
OCR_LANGUAGE = os.getenv('OCR_LANGUAGE', 'eng')
OCR_TIMEOUT = int(os.getenv('OCR_TIMEOUT', '300'))  # 5 minutes timeout

ACTION_INDICATORS = {
    'no_action_required': [
        'no specific assignment or transfer language found',
        'no assignment or transfer language found',
        'no specific requirements found',
        'no notification requirements found',
        'no assignment language found in contract',
        'no transfer language found in contract',
        'no assignment or transfer provisions',
        'no assignment clauses found',
        'no transfer clauses found',
        'contract does not contain assignment language',
        'contract does not contain transfer language',
        'no restrictions on assignment',
        'no restrictions on transfer',
        'assignment is not addressed',
        'transfer is not addressed',
        'no assignment or transfer language found in contract'
    ],
    'action_required': [
        'cannot be assigned',
        'prohibits assignment', 
        'requires consent',
        'requires approval',
        'requires notice',
        'prior written consent',
        'written approval',
        'assignment prohibited',
        'transfer prohibited',
        'no assignment without',
        'no transfer without',
        'requires prior written consent',
        'requires written consent',
        'requires approval',
        'consent required',
        'approval required'
    ]
}
