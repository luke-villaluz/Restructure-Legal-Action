import requests
import json
import importlib.util
from typing import Dict, Any, Optional
from config.settings import OLLAMA_MODEL, PROMPT_FILE
from utils.logger import logger
from core.text_filter import TextFilter
from core.ai_interface import AIAnalyzer
from core.response_parser import ResponseParser

class OllamaClient(AIAnalyzer):
    """Ollama implementation of AIAnalyzer interface"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = OLLAMA_MODEL
        self.logger = logger
        
    def test_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                self.logger.info("✅ Ollama connection successful")
                return True
            else:
                self.logger.error(f"❌ Ollama connection failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Cannot connect to Ollama: {e}")
            return False
    
    def analyze_company_documents(self, company_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Implementation of abstract method"""
        try:
            company_name = company_data.get('company_name', 'Unknown Company')
            combined_text = company_data.get('combined_text', '')
            search_terms = company_data.get('search_terms', [])
            
            if not combined_text:
                self.logger.warning(f"No text to analyze for {company_name}")
                return None
            
            return self._analyze_with_simple_approach(company_name, combined_text, search_terms)
            
        except Exception as e:
            self.logger.error(f"❌ Analysis failed for {company_name}: {e}")
            return None
    
    def _analyze_with_simple_approach(self, company_name: str, combined_text: str, search_terms: list) -> Optional[Dict[str, Any]]:
        """Use the bulletproof simple text approach with filtering"""
        try:
            # Filter text to relevant sections
            text_filter = TextFilter(search_terms, window_size=1000)
            filtered_text = combined_text #text_filter.filter_text(combined_text)
            
            if not filtered_text:
                self.logger.warning(f"No relevant text found for {company_name}")
                return None
            
            # Use filtered text in prompt
            try:
                spec = importlib.util.spec_from_file_location("prompt_module", PROMPT_FILE)
                prompt_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(prompt_module)
                ANALYSIS_PROMPT = prompt_module.ANALYSIS_PROMPT
                self.logger.info(f"✅ Loaded prompt from: {PROMPT_FILE}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load prompt from {PROMPT_FILE}: {e}")
                return None

            prompt = ANALYSIS_PROMPT.format(
                contract_text=filtered_text,
                search_terms=", ".join(search_terms)
            )
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 10000
                }
            }
            
            self.logger.info(f" Analyzing {company_name}")
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result.get('response', '')
                
                # Add debug logging
                self.logger.info(f"🔍 Raw LLM response for {company_name}:")
                self.logger.info(f"---START---")
                self.logger.info(analysis_text)
                self.logger.info(f"---END---")
                
                # Parse the simple format with bulletproof error handling
                return self._parse_detailed_response(analysis_text, company_name)
            else:
                self.logger.error(f"❌ Ollama API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            self.logger.error(f"❌ Analysis failed for {company_name}: {e}")
            return None

    def _parse_detailed_response(self, text: str, company_name: str) -> Dict[str, Any]:
        """Implementation of abstract method - uses shared parser"""
        return ResponseParser.parse_detailed_response(text, company_name)

# Convenience function for easy usage
def create_ollama_client() -> OllamaClient:
    """Create and return an Ollama client instance"""
    return OllamaClient()
