import requests
import json
from typing import Dict, Any, Optional
from config.settings import OLLAMA_MODEL
from utils.logger import logger

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
        Analyze all documents for a company
        
        Args:
            company_data: Dictionary containing:
                - company_name: Name of the company
                - combined_text: Combined text from all documents
                - document_stats: Statistics about documents processed
                - failed_documents: List of documents that failed to process
                - search_terms: List of terms to search for
        
        Returns:
            Dictionary with analysis results or None if failed
        """
        try:
            company_name = company_data.get('company_name', 'Unknown Company')
            combined_text = company_data.get('combined_text', '')
            search_terms = company_data.get('search_terms', [])
            document_stats = company_data.get('document_stats', {})
            failed_documents = company_data.get('failed_documents', [])
            
            if not combined_text:
                self.logger.warning(f"No text to analyze for {company_name}")
                return None
            
            # Prepare the prompt with document context
            from prompts.analysis_prompt import ANALYSIS_PROMPT
            prompt = ANALYSIS_PROMPT.format(
                contract_text=combined_text,
                search_terms=", ".join(search_terms)
            )
            
            # Add document processing information to the prompt
            if document_stats or failed_documents:
                prompt += f"\n\nDOCUMENT PROCESSING CONTEXT:\n"
                prompt += f"Total documents processed: {document_stats.get('total', 0)}\n"
                prompt += f"Successfully extracted: {document_stats.get('successful', 0)} documents\n"
                if failed_documents:
                    prompt += f"Failed to process: {len(failed_documents)} documents\n"
                    prompt += f"Failed documents: {', '.join(failed_documents)}\n"
                    prompt += f"Note: Analysis is based on successfully processed documents only.\n"
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent legal analysis
                    "top_p": 0.9,
                    "max_tokens": 8000  # Increased for longer documents
                }
            }
            
            self.logger.info(f"🤖 Sending document analysis request for {company_name}")
            
            # Send request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=300  # bumped to 5 minutes for increased max tokens
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result.get('response', '')
                
                # Parse the structured response
                parsed_analysis = self._parse_analysis_response(analysis_text, company_name)
                
                # Add document processing metadata
                parsed_analysis['document_stats'] = document_stats
                parsed_analysis['failed_documents'] = failed_documents
                
                self.logger.info(f"✅ Analysis completed for {company_name}")
                return parsed_analysis
                
            else:
                self.logger.error(f"❌ Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Request failed for {company_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Analysis failed for {company_name}: {e}")
            return None
    
    def analyze_contract(self, contract_text: str, search_terms: list, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Legacy method for backward compatibility - analyze single contract text
        
        Args:
            contract_text: The extracted text from the PDF
            search_terms: List of terms to search for
            company_name: Name of the company for context
            
        Returns:
            Dictionary with analysis results or None if failed
        """
        # Create company_data structure for the new method
        company_data = {
            'company_name': company_name,
            'combined_text': contract_text,
            'search_terms': search_terms,
            'document_stats': {'total': 1, 'successful': 1, 'failed': 0},
            'failed_documents': []
        }
        
        return self.analyze_company_documents(company_data)
    
    def _parse_analysis_response(self, response_text: str, company_name: str) -> Dict[str, Any]:
        """
        Parse the structured response from Ollama into a dictionary
        
        Args:
            response_text: Raw response from Ollama
            company_name: Company name for context
            
        Returns:
            Parsed analysis dictionary
        """
        try:
            # Initialize default structure
            analysis = {
                "company": company_name,
                "key_findings": [],
                "risk_assessment": [],
                "recommendations": [],
                "raw_response": response_text
            }
            
            # Parse the response line by line
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Detect sections (case insensitive)
                if "KEY FINDINGS:" in line.upper():
                    current_section = "key_findings"
                    continue
                elif "RISK ASSESSMENT:" in line.upper():
                    current_section = "risk_assessment"
                    continue
                elif "RECOMMENDATIONS:" in line.upper():
                    current_section = "recommendations"
                    continue
                elif "COMPANY:" in line.upper():
                    # Extract company name if provided
                    if ":" in line:
                        company = line.split(":", 1)[1].strip()
                        if company and company != "[Company Name]":
                            analysis["company"] = company
                    continue
                
                # Parse bullet points and numbered items
                if current_section and current_section in analysis:
                    # Look for bullet points (•, -, *, etc.)
                    if line.startswith(('•', '-', '*', '→', '⚠')):
                        content = line[1:].strip()
                        if content:
                            analysis[current_section].append(content)
                    # Look for numbered items
                    elif line[0].isdigit() and '.' in line[:3]:
                        content = line.split('.', 1)[1].strip()
                        if content:
                            analysis[current_section].append(content)
                    # Look for bracketed items (fallback)
                    elif line.startswith('[') and line.endswith(']'):
                        content = line[1:-1].strip()
                        if content and content != "[Finding 1 - specific clause or term identified]":
                            analysis[current_section].append(content)
                    # Look for lines that start with common legal terms
                    elif any(term in line.upper() for term in ['SECTION', 'CLAUSE', 'TERMINATION', 'LIABILITY', 'NOTICE', 'INDEMNIFICATION']):
                        if len(line) > 10:  # Only add if it's substantial content
                            analysis[current_section].append(line)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Failed to parse analysis response: {e}")
            # Return basic structure with raw response
            return {
                "company": company_name,
                "key_findings": ["Error parsing response"],
                "risk_assessment": ["Unable to assess risks"],
                "recommendations": ["Review raw response manually"],
                "raw_response": response_text
            }
    
    def get_available_models(self) -> list:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            self.logger.error(f"❌ Failed to get models: {e}")
            return []

# Convenience function for easy usage
def create_ollama_client() -> OllamaClient:
    """Create and return an Ollama client instance"""
    return OllamaClient()
