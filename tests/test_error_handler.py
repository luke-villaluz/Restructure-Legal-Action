import os
import sys

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.error_handler import ErrorHandler

def test_error_handler_initialization():
    """Test error handler initialization"""
    print("Testing error handler initialization...")
    
    try:
        handler = ErrorHandler()
        print("✅ Error handler initialization: PASS")
        return True
    except Exception as e:
        print(f"❌ Error handler initialization: FAIL - {e}")
        return False

def test_error_recovery():
    """Test error recovery functionality"""
    print("Testing error recovery...")
    
    try:
        handler = ErrorHandler()
        
        # Simulate a processing error
        error_context = {
            'company_name': 'Test Company',
            'step': 'PDF extraction',
            'error': 'File not found',
            'failed_documents': ['test.pdf'],
            'document_stats': {'total': 1, 'successful': 0, 'failed': 1}
        }
        
        # Test error handling
        result = handler.handle_processing_error(error_context)
        
        if result:
            print("✅ Error recovery: PASS")
            return True
        else:
            print("❌ Error recovery: FAIL")
            return False
            
    except Exception as e:
        print(f"❌ Error recovery: FAIL - {e}")
        return False

def test_placeholder_summary_creation():
    """Test creating placeholder summaries for failed companies"""
    print("Testing placeholder summary creation...")
    
    try:
        handler = ErrorHandler()
        
        # Test creating placeholder for failed company
        result = handler.create_error_summary('Failed Company', 'PDF extraction failed', ['doc1.pdf', 'doc2.pdf'])
        
        # Check if any error summary file exists (don't check exact filename)
        if result:
            # Look for any error summary file for this company
            output_dir = "data/summaries"
            if os.path.exists(output_dir):
                error_files = [f for f in os.listdir(output_dir) 
                             if 'Failed Company' in f and ('ERROR' in f or 'PROCESSING FAILED' in f)]
                if error_files:
                    print(f"✅ Placeholder summary creation: PASS - Found error file: {error_files[0]}")
                    return True
        
        print("❌ Placeholder summary creation: FAIL")
        return False
        
    except Exception as e:
        print(f"❌ Placeholder summary creation: FAIL - {e}")
        return False

def test_company_validation():
    """Test company data validation"""
    print("Testing company validation...")
    
    try:
        handler = ErrorHandler()
        
        # Test valid company data
        valid_company = {
            'company_name': 'Valid Company',
            'combined_text': 'This is valid text content',
            'document_stats': {'total': 2, 'successful': 2, 'failed': 0},
            'failed_documents': []
        }
        
        validation = handler.validate_company_processing(valid_company)
        if validation['is_valid']:
            print("✅ Valid company validation: PASS")
        else:
            print(f"❌ Valid company validation: FAIL - {validation['errors']}")
            return False
        
        # Test invalid company data
        invalid_company = {
            'company_name': '',
            'combined_text': '',
            'document_stats': {'total': 0, 'successful': 0, 'failed': 0},
            'failed_documents': []
        }
        
        validation = handler.validate_company_processing(invalid_company)
        if not validation['is_valid']:
            print("✅ Invalid company validation: PASS")
        else:
            print("❌ Invalid company validation: FAIL - Should have detected invalid data")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Company validation: FAIL - {e}")
        return False

def test_processing_summary_logging():
    """Test processing summary logging"""
    print("Testing processing summary logging...")
    
    try:
        handler = ErrorHandler()
        
        # Test logging processing summary
        failed_details = [
            {'name': 'Company A', 'error': 'PDF extraction failed'},
            {'name': 'Company B', 'error': 'Ollama connection failed'}
        ]
        
        # This should log without errors
        handler.log_processing_summary(
            total_companies=10,
            successful_companies=8,
            failed_companies=2,
            failed_company_details=failed_details
        )
        
        print("✅ Processing summary logging: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Processing summary logging: FAIL - {e}")
        return False

if __name__ == "__main__":
    test_error_handler_initialization()
    test_error_recovery()
    test_placeholder_summary_creation()
    test_company_validation()
    test_processing_summary_logging()
