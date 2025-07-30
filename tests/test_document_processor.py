import os
import sys

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.document_processor import DocumentProcessor
from config.settings import TEST_FOLDER

def test_data_structure_scanning():
    """Test scanning data structure - count folders in Vendor and Client directories"""
    print("Testing data structure scanning...")
    
    try:
        # Check Vendors folder
        vendors_path = "data/Vendors"
        if os.path.exists(vendors_path):
            vendor_folders = [f for f in os.listdir(vendors_path) if os.path.isdir(os.path.join(vendors_path, f))]
            print(f"✅ Vendors folder: {len(vendor_folders)} subfolders found")
            for folder in vendor_folders:
                print(f"   - {folder}")
        else:
            print("❌ Vendors folder not found")
        
        # Check Clients folder  
        clients_path = "data/Clients"
        if os.path.exists(clients_path):
            client_folders = [f for f in os.listdir(clients_path) if os.path.isdir(os.path.join(clients_path, f))]
            print(f"✅ Clients folder: {len(client_folders)} subfolders found")
            for folder in client_folders:
                print(f"   - {folder}")
        else:
            print("❌ Clients folder not found")
        
        return True
    except Exception as e:
        print(f"❌ Data structure scanning: FAIL - {e}")
        return False

def test_document_discovery():
    """Test discovering documents in the test folder"""
    print(f"Testing document discovery in: {TEST_FOLDER}")
    
    if not TEST_FOLDER:
        print("❌ TEST_FOLDER not set in .env")
        return False
    
    processor = DocumentProcessor()
    
    try:
        # Find all documents in the test folder
        if not os.path.exists(TEST_FOLDER):
            print(f"❌ Test folder {TEST_FOLDER} does not exist")
            return False
        
        document_files = processor.get_all_documents_in_folder(TEST_FOLDER)
        
        if len(document_files) == 0:
            print(f"❌ No documents found in {TEST_FOLDER}")
            return False
        
        print(f"✅ Document discovery: PASS - Found {len(document_files)} documents")
        for doc in document_files:
            print(f"   - {os.path.basename(doc)}")
        
        return True
    except Exception as e:
        print(f"❌ Document discovery: FAIL - {e}")
        return False

def test_text_extraction():
    """Test extracting text from documents in the test folder"""
    print(f"Testing text extraction from: {TEST_FOLDER}")
    
    if not TEST_FOLDER:
        print("❌ TEST_FOLDER not set in .env")
        return False
    
    processor = DocumentProcessor()
    
    try:
        # Extract text from all documents
        result = processor.extract_all_text_from_folder(TEST_FOLDER)
        
        successful_texts = result.get('successful_texts', {})
        failed_documents = result.get('failed_documents', [])
        document_stats = result.get('document_stats', {})
        
        if len(successful_texts) == 0:
            print(f"❌ No text extracted from {TEST_FOLDER}")
            return False
        
        print(f"✅ Text extraction: PASS - Extracted from {len(successful_texts)} documents")
        print(f"Document stats: {document_stats}")
        
        if failed_documents:
            print(f"Failed documents: {failed_documents}")
        
        # Show sample of combined text
        combined_text = processor.combine_document_texts(successful_texts)
        print(f"Combined text length: {len(combined_text)} characters")
        print(f"First 200 chars: {combined_text[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Text extraction: FAIL - {e}")
        return False

def test_ocr_extraction():
    """Test EasyOCR text extraction from scanned PDFs"""
    print("Testing EasyOCR extraction...")
    
    if not TEST_FOLDER:
        print("❌ TEST_FOLDER not set in .env")
        return False
    
    processor = DocumentProcessor()
    
    try:
        # Find PDF files in test folder
        pdf_files = [f for f in os.listdir(TEST_FOLDER) 
                    if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print("❌ No PDF files found for OCR testing")
            return False
        
        # Test OCR on first PDF
        test_pdf = os.path.join(TEST_FOLDER, pdf_files[0])
        print(f"Testing EasyOCR on: {pdf_files[0]}")
        
        # Try OCR extraction
        ocr_text = processor._extract_text_with_ocr(test_pdf)
        
        if ocr_text:
            print(f"✅ EasyOCR extraction: PASS - Extracted {len(ocr_text)} characters")
            print(f"First 200 chars: {ocr_text[:200]}...")
            return True
        else:
            print("❌ EasyOCR extraction: FAIL - No text extracted")
            return False
            
    except Exception as e:
        print(f"❌ EasyOCR extraction: FAIL - {e}")
        return False

if __name__ == "__main__":
    test_data_structure_scanning()
    test_document_discovery()
    test_text_extraction()
    test_ocr_extraction()  # Add this line
