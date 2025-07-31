import requests
import os
import sys
sys.path.append('..')  # Add parent directory to path

from dotenv import load_dotenv

load_dotenv()

def test_perplexity_api():
    """Test Perplexity API connection"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    print(f"API Key found: {api_key[:10]}..." if api_key else "No API key found!")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Use the correct model name from Perplexity docs
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }

    print("Testing Perplexity API...")
    print(f"URL: https://api.perplexity.ai/chat/completions")
    print(f"Model: sonar-pro")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")

    response = requests.post("https://api.perplexity.ai/chat/completions", 
                            json=payload, 
                            headers=headers)

    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ API key is valid!")
        return True
    else:
        print("❌ API key is invalid or has issues!")
        return False

if __name__ == "__main__":
    test_perplexity_api()
