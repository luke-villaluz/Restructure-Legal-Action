"""Test suite for document processing functionality."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.document_processor import DocumentProcessor
from config.settings import TEST_FOLDER

class TestDocumentProcessor(unittest.TestCase):
    """Test cases for DocumentProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = DocumentProcessor()
        self.test_folder = TEST_FOLDER
    
    def test_is_document_file(self):
        """Test document file type detection."""
        # Valid document files
        self.assertTrue(self.processor.is_document_file("test.pdf"))
        self.assertTrue(self.processor.is_document_file("test.docx"))
        self.assertTrue(self.processor.is_document_file("test.doc"))
        self.assertTrue(self.processor.is_document_file("TEST.PDF"))
        
        # Invalid files
        self.assertFalse(self.processor.is_document_file("test.txt"))
        self.assertFalse(self.processor.is_document_file("test.jpg"))
        self.assertFalse(self.processor.is_document_file("test"))
    
    def test_get_all_documents_in_folder(self):
        """Test document discovery in folder."""
        if not self.test_folder or not os.path.exists(self.test_folder):
            self.skipTest("TEST_FOLDER not configured or does not exist")
        
        documents = self.processor.get_all_documents_in_folder(self.test_folder)
        self.assertIsInstance(documents, list)
        
        # Verify all returned files are valid documents
        for doc_path in documents:
            self.assertTrue(os.path.exists(doc_path))
            self.assertTrue(self.processor.is_document_file(doc_path))
    
    @patch('core.document_processor.OCR_AVAILABLE', False)
    def test_pdf_extraction_without_ocr(self):
        """Test PDF extraction when OCR dependencies are not available."""
        result = self.processor.extract_text_from_pdf("test.pdf")
        self.assertIsNone(result)
    
    def test_extract_all_text_from_folder(self):
        """Test complete text extraction workflow."""
        if not self.test_folder or not os.path.exists(self.test_folder):
            self.skipTest("TEST_FOLDER not configured or does not exist")
        
        result = self.processor.extract_all_text_from_folder(self.test_folder)
        
        # Verify result structure
        self.assertIn('successful_texts', result)
        self.assertIn('failed_documents', result)
        self.assertIn('document_stats', result)
        
        # Verify stats are consistent
        stats = result['document_stats']
        self.assertEqual(
            stats['total'],
            stats['successful'] + stats['failed']
        )
    
    def test_combine_document_texts(self):
        """Test document text combination."""
        test_texts = {
            "doc1.pdf": "Content from document 1",
            "doc2.docx": "Content from document 2"
        }
        
        combined = self.processor.combine_document_texts(test_texts)
        
        self.assertIn("=== DOCUMENT: doc1.pdf ===", combined)
        self.assertIn("=== DOCUMENT: doc2.docx ===", combined)
        self.assertIn("Content from document 1", combined)
        self.assertIn("Content from document 2", combined)
    
    def test_combine_empty_document_texts(self):
        """Test combining empty document texts."""
        result = self.processor.combine_document_texts({})
        self.assertEqual(result, "")
    
    def test_extract_all_text_from_nonexistent_folder(self):
        """Test extraction from non-existent folder."""
        result = self.processor.extract_all_text_from_folder("/nonexistent/folder")
        
        self.assertEqual(result['successful_texts'], {})
        self.assertEqual(result['failed_documents'], [])
        self.assertEqual(result['document_stats']['total'], 0)

def run_document_processor_tests():
    """Run document processor tests with detailed output."""
    print("Running Document Processor Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDocumentProcessor)
    
    # Run tests with custom runner
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_document_processor_tests()
