"""Perplexity AI client for contract analysis."""

import requests
import json
import importlib.util
from typing import Dict, Any, Optional
from config.settings import PERPLEXITY_MODEL, PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL, PROMPT_FILE
from utils.logger import logger
from core.text_filter import TextFilter
from core.ai_interface import AIAnalyzer
from core.response_parser import ResponseParser

class PerplexityClient(AIAnalyzer):
    """Perplexity implementation of AIAnalyzer interface."""
    
    def __init__(self):
        self.model = PERPLEXITY_MODEL
        self.api_key = PERPLEXITY_API_KEY
        self.base_url = PERPLEXITY_BASE_URL
        self.logger = logger
        
    def test_connection(self) -> bool:
        """Test if Perplexity API is accessible."""
        headers = self._get_headers()
        test_payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions", 
                json=test_payload, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info("Perplexity connection successful")
                return True
            
            self.logger.error(f"Perplexity connection failed: {response.status_code}")
            return False
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Cannot connect to Perplexity: {e}")
            return False
    
    def analyze_company_documents(self, company_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze company documents using Perplexity API."""
        company_name = company_data.get('company_name', 'Unknown Company')
        combined_text = company_data.get('combined_text', '')
        search_terms = company_data.get('search_terms', [])
        
        if not combined_text:
            self.logger.warning(f"No text to analyze for {company_name}")
            return None
        
        return self._analyze_with_perplexity(company_name, combined_text, search_terms)
    
    def _analyze_with_perplexity(self, company_name: str, combined_text: str, search_terms: list) -> Optional[Dict[str, Any]]:
        """Use Perplexity API for analysis."""
        text_filter = TextFilter(search_terms, window_size=1000)
        filtered_text = combined_text  # text_filter.filter_text(combined_text)
        
        if not filtered_text:
            self.logger.warning(f"No relevant text found for {company_name}")
            return None
        
        analysis_prompt = self._load_analysis_prompt()
        if not analysis_prompt:
            return None
        
        prompt = analysis_prompt.format(
            contract_text=filtered_text,
            search_terms=", ".join(search_terms)
        )
        
        headers = self._get_headers()
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        self.logger.info(f"Analyzing {company_name} with Perplexity")
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions", 
                json=payload, 
                headers=headers, 
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                
                self.logger.info(f"Raw Perplexity response for {company_name}:")
                self.logger.info(f"---START---")
                self.logger.info(analysis_text)
                self.logger.info(f"---END---")
                
                return self._parse_detailed_response(analysis_text, company_name)
            
            self.logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            self.logger.error(f"Analysis failed for {company_name}: {e}")
            return None

    def _parse_detailed_response(self, text: str, company_name: str) -> Dict[str, Any]:
        """Parse AI response into structured format."""
        return ResponseParser.parse_detailed_response(text, company_name)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers for Perplexity API."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _load_analysis_prompt(self) -> Optional[str]:
        """Load analysis prompt from file."""
        try:
            spec = importlib.util.spec_from_file_location("prompt_module", PROMPT_FILE)
            prompt_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(prompt_module)
            self.logger.info(f"Loaded prompt from: {PROMPT_FILE}")
            return prompt_module.ANALYSIS_PROMPT
        except Exception as e:
            self.logger.error(f"Failed to load prompt from {PROMPT_FILE}: {e}")
            return None

def create_perplexity_client() -> PerplexityClient:
    """Create and return a Perplexity client instance."""
    return PerplexityClient()
