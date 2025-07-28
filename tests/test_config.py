import os
import sys

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.settings import *

def test_config_loading():
    """Test that all environment variables load correctly"""
    print("Testing configuration loading...")
    
    print(f"INPUT_DIRECTORY: {INPUT_DIRECTORY}")
    print(f"OLLAMA_MODEL: {OLLAMA_MODEL}")
    print(f"SEARCH_TERMS: {SEARCH_TERMS}")
    print(f"LOG_LEVEL: {LOG_LEVEL}")
    
    # Basic checks
    if INPUT_DIRECTORY is None:
        print("❌ INPUT_DIRECTORY is None")
        return False
    if OLLAMA_MODEL is None:
        print("❌ OLLAMA_MODEL is None")
        return False
    if not isinstance(SEARCH_TERMS, list):
        print("❌ SEARCH_TERMS is not a list")
        return False
    
    print("✅ Configuration loading: PASS")
    return True

if __name__ == "__main__":
    test_config_loading()
