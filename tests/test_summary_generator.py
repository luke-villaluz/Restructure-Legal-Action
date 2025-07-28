import os
import sys

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.summary_generator import SummaryGenerator
from config.settings import OUTPUT_DIR

def test_summary_generator_initialization():
    """Test summary generator initialization"""
    print("Testing summary generator initialization...")
    
    try:
        generator = SummaryGenerator()
        print("✅ Summary generator initialization: PASS")
        return True
    except Exception as e:
        print(f"❌ Summary generator initialization: FAIL - {e}")
        return False

def test_summary_creation():
    """Test creating a summary PDF"""
    print("Testing summary creation...")
    
    # Sample analysis data (like what the LLM client would return)
    sample_analysis = {
        "company": "Test Company",
        "key_findings": [
            "Termination clause found in Section 3.2",
            "Liability provision identified in Section 5.1",
            "Notice requirement of 30 days specified"
        ],
        "risk_assessment": [
            "High risk - immediate termination possible",
            "Moderate risk - liability caps at $100,000"
        ],
        "recommendations": [
            "Review termination clauses carefully",
            "Consider negotiating liability limits"
        ],
        "raw_response": "Full AI response text here..."
    }
    
    try:
        generator = SummaryGenerator()
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Generate summary
        output_path = generator.create_summary_pdf(sample_analysis)
        
        if os.path.exists(output_path):
            print(f"✅ Summary creation: PASS - Created {output_path}")
            return True
        else:
            print("❌ Summary creation: FAIL - File not created")
            return False
            
    except Exception as e:
        print(f"❌ Summary creation: FAIL - {e}")
        return False

# Add test for document processing metadata
def test_summary_with_document_metadata():
    """Test creating summary with document processing metadata"""
    print("Testing summary with document metadata...")
    
    # Sample analysis data with document stats
    sample_analysis = {
        "company": "Test Company",
        "key_findings": [
            "Termination clause found in Section 3.2",
            "Liability provision identified in Section 5.1"
        ],
        "risk_assessment": [
            "High risk - immediate termination possible"
        ],
        "recommendations": [
            "Review termination clauses carefully"
        ],
        "document_stats": {
            "total": 5,
            "successful": 3,
            "failed": 2
        },
        "failed_documents": [
            "image-based-invoice.pdf",
            "corrupted-document.pdf"
        ],
        "raw_response": "Full AI response text here..."
    }
    
    try:
        generator = SummaryGenerator()
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Generate summary
        output_path = generator.create_summary_pdf(sample_analysis)
        
        if os.path.exists(output_path):
            print(f"✅ Summary creation with metadata: PASS - Created {output_path}")
            return True
        else:
            print("❌ Summary creation with metadata: FAIL - File not created")
            return False
            
    except Exception as e:
        print(f"❌ Summary creation with metadata: FAIL - {e}")
        return False

if __name__ == "__main__":
    test_summary_generator_initialization()
    test_summary_creation()
    test_summary_with_document_metadata() 