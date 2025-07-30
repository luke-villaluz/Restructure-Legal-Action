import requests
import json
from typing import Dict, Any, Optional
from config.settings import OLLAMA_MODEL
from utils.logger import logger
from core.text_filter import TextFilter

class OllamaClient:
    """Client for interacting with Ollama API"""
    
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
        """
        Analyze all documents for a company and return structured data
        
        Args:
            company_data: Dictionary containing:
                - company_name: Name of the company
                - combined_text: Combined text from all documents
                - search_terms: List of terms to search for
        
        Returns:
            Dictionary with structured analysis results or None if failed
        """
        try:
            company_name = company_data.get('company_name', 'Unknown Company')
            combined_text = company_data.get('combined_text', '')
            search_terms = company_data.get('search_terms', [])
            
            if not combined_text:
                self.logger.warning(f"No text to analyze for {company_name}")
                return None
            
            # Use the bulletproof simple approach
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
            from prompts.analysis_prompt import ANALYSIS_PROMPT
            prompt = ANALYSIS_PROMPT.format(
                contract_text=filtered_text,
                search_terms=", ".join(search_terms)
            )
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent responses
                    "top_p": 0.9,
                    "max_tokens": 10000   # Reasonable limit for simple responses
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
        """Parse the detailed response format"""
        try:
            # Initialize with defaults
            result = {
                'company': company_name,
                'name_change_requires_notification': 'Not Specified',
                'name_change_assignment': 'Unclear',
                'assignment_clause_reference': '',
                'material_corporate_structure': 'No',
                'notices_clause_present': 'No',
                'action_required': 'No Action Required',
                'recommended_action': 'No Action'
            }
            
            # Parse each line
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    # Map the keys to our result dictionary
                    if 'name change requires notification' in key:
                        result['name_change_requires_notification'] = value
                    elif 'name change considered an assignment' in key:
                        result['name_change_assignment'] = value
                    elif 'assignment clause reference' in key:
                        result['assignment_clause_reference'] = value
                    elif 'contract require notification for changes to corporate status' in key:
                        result['material_corporate_structure'] = value
                    elif 'notices clause present' in key:
                        result['notices_clause_present'] = value
                    elif 'action required prior to name change' in key:
                        result['action_required'] = value
                    elif 'recommended action' in key:
                        result['recommended_action'] = value
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing detailed response for {company_name}: {e}")
            return {
                'company': company_name,
                'name_change_requires_notification': 'Not Specified',
                'name_change_assignment': 'Unclear',
                'assignment_clause_reference': '',
                'material_corporate_structure': 'No',
                'notices_clause_present': 'No',
                'action_required': 'No Action Required',
                'recommended_action': 'No Action'
            }

# Convenience function for easy usage
def create_ollama_client() -> OllamaClient:
    """Create and return an Ollama client instance"""
    return OllamaClient()
