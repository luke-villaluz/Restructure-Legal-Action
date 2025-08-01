import requests
import json
from typing import Dict, Any, Optional
from config.settings import PERPLEXITY_MODEL, PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL
from utils.logger import logger
from core.text_filter import TextFilter
from core.ai_interface import AIAnalyzer
from core.response_parser import ResponseParser

class PerplexityClient(AIAnalyzer):
    """Perplexity implementation of AIAnalyzer interface"""
    
    def __init__(self):
        self.model = PERPLEXITY_MODEL
        self.api_key = PERPLEXITY_API_KEY
        self.base_url = PERPLEXITY_BASE_URL
        self.logger = logger
        
    def test_connection(self) -> bool:
        """Test if Perplexity API is accessible"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Simple test request
            test_payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(f"{self.base_url}/chat/completions", 
                                   json=test_payload, 
                                   headers=headers, 
                                   timeout=30)
            
            if response.status_code == 200:
                self.logger.info("✅ Perplexity connection successful")
                return True
            else:
                self.logger.error(f"❌ Perplexity connection failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Cannot connect to Perplexity: {e}")
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
            
            return self._analyze_with_perplexity(company_name, combined_text, search_terms)
            
        except Exception as e:
            self.logger.error(f"❌ Analysis failed for {company_name}: {e}")
            return None
    
    def _analyze_with_perplexity(self, company_name: str, combined_text: str, search_terms: list) -> Optional[Dict[str, Any]]:
        """Use Perplexity API for analysis"""
        try:
            # Filter text to relevant sections
            text_filter = TextFilter(search_terms, window_size=1000)
            filtered_text = combined_text  # text_filter.filter_text(combined_text)
            
            if not filtered_text:
                self.logger.warning(f"No relevant text found for {company_name}")
                return None
            
            # Use filtered text in prompt
            from prompts.analysis_prompt import ANALYSIS_PROMPT
            prompt = ANALYSIS_PROMPT.format(
                contract_text=filtered_text,
                search_terms=", ".join(search_terms)
            )
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.1,
                "top_p": 0.9
            }
            
            self.logger.info(f"�� Analyzing {company_name} with Perplexity")
            
            response = requests.post(f"{self.base_url}/chat/completions", 
                                   json=payload, 
                                   headers=headers, 
                                   timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                
                # Add debug logging
                self.logger.info(f"🔍 Raw Perplexity response for {company_name}:")
                self.logger.info(f"---START---")
                self.logger.info(analysis_text)
                self.logger.info(f"---END---")
                
                # Parse the response
                return self._parse_detailed_response(analysis_text, company_name)
            else:
                self.logger.error(f"❌ Perplexity API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            self.logger.error(f"❌ Analysis failed for {company_name}: {e}")
            return None

    def _parse_detailed_response(self, text: str, company_name: str) -> Dict[str, Any]:
        """Implementation of abstract method - uses shared parser"""
        return ResponseParser.parse_detailed_response(text, company_name)

# Convenience function for easy usage
def create_perplexity_client() -> PerplexityClient:
    """Create and return a Perplexity client instance"""
    return PerplexityClient()
