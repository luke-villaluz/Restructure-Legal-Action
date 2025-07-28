import os
import sys

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.llm_client import create_ollama_client
from config.settings import SEARCH_TERMS

def test_ollama_connection():
    """Test Ollama connection"""
    print("Testing Ollama connection...")
    
    client = create_ollama_client()
    if client.test_connection():
        print("✅ Ollama connection: PASS")
        return True
    else:
        print("❌ Ollama connection: FAIL")
        return False

def test_company_document_analysis():
    """Test analyzing company documents"""
    print("Testing company document analysis...")
    
    client = create_ollama_client()
    
    # Sample company data with multiple documents
    company_data = {
        'company_name': 'Test Company',
        'combined_text': 'This company has multiple contracts with termination clauses and liability provisions.',
        'search_terms': SEARCH_TERMS,
        'document_stats': {
            'total': 3,
            'successful': 2,
            'failed': 1
        },
        'failed_documents': ['image-based-invoice.pdf']
    }
    
    result = client.analyze_company_documents(company_data)
    
    if result is not None:
        print(f"✅ Company analysis: PASS")
        print(f"   Company: {result.get('company')}")
        print(f"   Findings: {len(result.get('key_findings', []))}")
        print(f"   Document stats: {result.get('document_stats')}")
        return True
    else:
        print("❌ Company analysis: FAIL")
        return False

def test_legacy_contract_analysis():
    """Test legacy single contract analysis"""
    print("Testing legacy contract analysis...")
    
    client = create_ollama_client()
    test_text = "This contract contains termination clauses and liability provisions."
    result = client.analyze_contract(test_text, SEARCH_TERMS, "Test Company")
    
    if result is not None:
        print(f"✅ Legacy analysis: PASS")
        return True
    else:
        print("❌ Legacy analysis: FAIL")
        return False

if __name__ == "__main__":
    test_ollama_connection()
    test_company_document_analysis()
    test_legacy_contract_analysis()
