"""Parse AI responses into structured data."""

import json
import re
from typing import Dict, Any, Optional
from utils.logger import logger

class ResponseParser:
    """Parse AI responses into structured contract analysis data."""
    
    @staticmethod
    def parse_detailed_response(text: str, company_name: str) -> Dict[str, Any]:
        """Parse JSON response with fallback to text extraction."""
        text = text.strip()
        
        # Remove markdown code blocks
        text = ResponseParser._clean_markdown(text)
        
        # Try JSON parsing first
        json_data = ResponseParser._extract_json(text)
        if json_data:
            logger.info(f"JSON parsing successful for {company_name}")
            return ResponseParser._build_result_from_json(json_data, company_name)
        
        # Fallback to text extraction
        logger.info(f"Using fallback extraction for {company_name}")
        return ResponseParser._extract_from_text_fallback(text, company_name)
    
    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Remove markdown code blocks from text."""
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        return text.strip()
    
    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from text."""
        json_start = text.find('{')
        json_end = text.rfind('}')
        
        if json_start == -1 or json_end == -1 or json_end <= json_start:
            return None
        
        json_text = text[json_start:json_end + 1]
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def _build_result_from_json(data: Dict[str, Any], company_name: str) -> Dict[str, Any]:
        """Build result from JSON data."""
        def clean_value(value):
            return str(value).strip() if value else 'Not Specified'
        
        return {
            'company': company_name,
            'contract_name': clean_value(data.get('contract_name')),
            'effective_date': clean_value(data.get('effective_date')),
            'renewal_termination_date': clean_value(data.get('renewal_termination_date')),
            'assignment_clause_reference': clean_value(data.get('assignment_clause_reference')),
            'notices_clause_present': clean_value(data.get('notices_clause_present')),
            'action_required': clean_value(data.get('action_required')),
            'recommended_action': clean_value(data.get('recommended_action')),
            'contact_listed': clean_value(data.get('contact_listed'))
        }
    
    @staticmethod
    def _extract_from_text_fallback(text: str, company_name: str) -> Dict[str, Any]:
        """Extract data directly from text when JSON fails."""
        result = ResponseParser._get_default_result(company_name)
        
        patterns = {
            'contract_name': r'"([^"]+)"',
            'effective_date': r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d{1,2},? \d{4})',
            'action_required': r'(Notification Required|Consent Required|No Action Required|Further Legal Review Recommended)',
            'recommended_action': r'(Send Notification|Request Consent|No Action|Escalate for Legal Review)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result[field] = match.group(1)
        
        return result
    
    @staticmethod
    def _get_default_result(company_name: str) -> Dict[str, Any]:
        """Return default result structure."""
        return {
            'company': company_name,
            'contract_name': 'Not Specified',
            'effective_date': 'Not Specified',
            'renewal_termination_date': 'Not Specified',
            'assignment_clause_reference': 'N/A',
            'notices_clause_present': 'Not Specified',
            'action_required': 'Not Specified',
            'recommended_action': 'Not Specified',
            'contact_listed': 'Not Specified'
        }
