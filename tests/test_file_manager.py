import os
import sys

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.file_manager import FileManager
from config.settings import TEST_FOLDER

def test_file_manager_initialization():
    """Test file manager initialization"""
    print("Testing file manager initialization...")
    
    try:
        manager = FileManager()
        print("✅ File manager initialization: PASS")
        return True
    except Exception as e:
        print(f"❌ File manager initialization: FAIL - {e}")
        return False

def test_company_discovery():
    """Test discovering company folders"""
    print("Testing company discovery...")
    
    try:
        manager = FileManager()
        
        # Get all company folders
        companies = manager.get_all_companies()
        
        print(f"✅ Company discovery: PASS - Found {len(companies)} companies")
        for company in companies:
            print(f"   - {company['name']} ({company['type']}) - {company['path']}")
        
        return True
    except Exception as e:
        print(f"❌ Company discovery: FAIL - {e}")
        return False

def test_document_discovery():
    """Test discovering documents in a company folder"""
    print("Testing document discovery...")
    
    try:
        manager = FileManager()
        
        # Get first company for testing
        companies = manager.get_all_companies()
        if len(companies) == 0:
            print("❌ No companies found to test")
            return False
        
        test_company = companies[0]
        print(f"Testing with company: {test_company['name']}")
        
        # Test getting documents for this company
        documents = manager.get_company_documents(test_company['path'])
        if documents:
            print(f"✅ Document discovery: PASS - Found {len(documents)} documents")
            for doc in documents[:3]:  # Show first 3 documents
                print(f"   - {os.path.basename(doc)}")
            if len(documents) > 3:
                print(f"   ... and {len(documents) - 3} more")
            return True
        else:
            print(f"❌ Document discovery: FAIL - No documents found")
            return False
            
    except Exception as e:
        print(f"❌ Document discovery: FAIL - {e}")
        return False

def test_combined_text_extraction():
    """Test extracting combined text from a company folder"""
    print("Testing combined text extraction...")
    
    try:
        manager = FileManager()
        
        # Get first company for testing
        companies = manager.get_all_companies()
        if len(companies) == 0:
            print("❌ No companies found to test")
            return False
        
        test_company = companies[0]
        print(f"Testing with company: {test_company['name']}")
        
        # Test getting combined text for this company
        result = manager.get_company_combined_text(test_company['path'])
        
        if result and result.get('combined_text'):
            combined_text = result['combined_text']
            document_stats = result.get('document_stats', {})
            failed_documents = result.get('failed_documents', [])
            
            print(f"✅ Combined text extraction: PASS - {len(combined_text)} characters")
            print(f"Document stats: {document_stats}")
            if failed_documents:
                print(f"Failed documents: {failed_documents}")
            print(f"First 200 chars: {combined_text[:200]}...")
            return True
        else:
            print(f"❌ Combined text extraction: FAIL - No text extracted")
            return False
            
    except Exception as e:
        print(f"❌ Combined text extraction: FAIL - {e}")
        return False

if __name__ == "__main__":
    test_file_manager_initialization()
    test_company_discovery()
    test_document_discovery()
    test_combined_text_extraction()
