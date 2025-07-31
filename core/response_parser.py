import json
import re
from typing import Dict, Any
from utils.logger import logger

class ResponseParser:
    @staticmethod
    def parse_detailed_response(text: str, company_name: str) -> Dict[str, Any]:
        """Parse JSON response - handle extra text after JSON"""
        try:
            # Clean the response
            text = text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            
            text = text.strip()
            
            # Find the JSON object - look for opening and closing braces
            json_start = text.find('{')
            json_end = text.rfind('}')
            
            if json_start != -1 and json_end != -1 and json_end > json_start:
                # Extract just the JSON part
                json_text = text[json_start:json_end + 1]
                
                try:
                    data = json.loads(json_text)
                    logger.info(f"✅ JSON parsing successful for {company_name}")
                    return ResponseParser._build_result_from_json(data, company_name)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing failed for {company_name}: {e}")
            
            # Fallback: extract data from text directly
            logger.info(f"🔄 Using fallback extraction for {company_name}")
            return ResponseParser._extract_from_text_fallback(text, company_name)
            
        except Exception as e:
            logger.error(f"❌ All parsing failed for {company_name}: {e}")
            return ResponseParser._get_default_result(company_name)
    
    @staticmethod
    def _build_result_from_json(data: Dict[str, Any], company_name: str) -> Dict[str, Any]:
        """Build result from JSON data"""
        def clean_value(value):
            if not value or value == '':
                return 'Not Specified'
            return str(value).strip()
        
        return {
            'company': company_name,
            'contract_name': clean_value(data.get('contract_name')),
            'contract_counterparty': clean_value(data.get('contract_counterparty')),
            'effective_date': clean_value(data.get('effective_date')),
            'renewal_termination_date': clean_value(data.get('renewal_termination_date')),
            'name_change_requires_notification': clean_value(data.get('name_change_requires_notification')),
            'clause_reference': clean_value(data.get('clause_reference')),
            'is_assignment': clean_value(data.get('is_assignment')),
            'assignment_clause_reference': clean_value(data.get('assignment_clause_reference')),
            'material_corporate_structure_clauses': clean_value(data.get('material_corporate_structure_clauses')),
            'notices_clause_present': clean_value(data.get('notices_clause_present')),
            'action_required': clean_value(data.get('action_required')),
            'recommended_action': clean_value(data.get('recommended_action'))
        }
    
    @staticmethod
    def _extract_from_text_fallback(text: str, company_name: str) -> Dict[str, Any]:
        """Extract data directly from text when JSON fails"""
        result = ResponseParser._get_default_result(company_name)
        
        # Look for specific patterns in the text
        patterns = {
            'contract_name': r'"([^"]+)"',
            'contract_counterparty': r'"([^"]+)"',
            'effective_date': r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d{1,2},? \d{4})',
            'name_change_requires_notification': r'(Yes|No|Not Specified)',
            'is_assignment': r'(Yes|No|Unclear)',
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
        return {
            'company': company_name,
            'contract_name': 'Not Specified',
            'contract_counterparty': 'Not Specified',
            'effective_date': 'Not Specified',
            'renewal_termination_date': 'Not Specified',
            'name_change_requires_notification': 'Not Specified',
            'clause_reference': 'N/A',
            'is_assignment': 'Not Specified',
            'assignment_clause_reference': 'N/A',
            'material_corporate_structure_clauses': 'Not Specified',
            'notices_clause_present': 'Not Specified',
            'action_required': 'Not Specified',
            'recommended_action': 'Not Specified'
        }
