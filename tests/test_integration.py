"""Integration tests for the complete legal analysis workflow."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.file_manager import FileManager
from core.excel_generator import ExcelGenerator
from core.response_parser import ResponseParser
from config.settings import TEST_FOLDER

class TestIntegration(unittest.TestCase):
    """Integration test cases for the complete workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()
        self.excel_generator = ExcelGenerator()
        self.test_folder = TEST_FOLDER
    
    def test_file_manager_initialization(self):
        """Test FileManager initialization."""
        self.assertIsNotNone(self.file_manager.base_path)
        self.assertIsNotNone(self.file_manager.logger)
    
    def test_excel_generator_initialization(self):
        """Test ExcelGenerator initialization."""
        self.assertIsNotNone(self.excel_generator.output_dir)
        self.assertIsNotNone(self.excel_generator.logger)
    
    def test_response_parser_json_extraction(self):
        """Test JSON response parsing."""
        test_json = '''
        {
            "contract_name": "Test Contract",
            "effective_date": "2024-01-01",
            "renewal_termination_date": "2025-01-01",
            "assignment_clause_reference": "Section 5.2",
            "notices_clause_present": "Yes",
            "action_required": "Notification Required",
            "recommended_action": "Send notification within 30 days"
        }
        '''
        
        result = ResponseParser.parse_detailed_response(test_json, "Test Company")
        
        self.assertEqual(result['company'], "Test Company")
        self.assertEqual(result['contract_name'], "Test Contract")
        self.assertEqual(result['effective_date'], "2024-01-01")
        self.assertEqual(result['action_required'], "Notification Required")
    
    def test_response_parser_markdown_cleaning(self):
        """Test markdown code block cleaning."""
        test_text = '```json\n{"contract_name": "Test"}\n```'
        
        result = ResponseParser.parse_detailed_response(test_text, "Test Company")
        
        self.assertEqual(result['contract_name'], "Test")
    
    def test_response_parser_fallback_extraction(self):
        """Test fallback text extraction when JSON fails."""
        test_text = 'Contract name is "Test Contract" and action required is Notification Required'
        
        result = ResponseParser.parse_detailed_response(test_text, "Test Company")
        
        self.assertEqual(result['contract_name'], "Test Contract")
        self.assertEqual(result['action_required'], "Notification Required")
    
    def test_response_parser_default_result(self):
        """Test default result when parsing completely fails."""
        test_text = "Invalid text with no useful information"
        
        result = ResponseParser.parse_detailed_response(test_text, "Test Company")
        
        self.assertEqual(result['company'], "Test Company")
        self.assertEqual(result['contract_name'], "Not Specified")
        self.assertEqual(result['action_required'], "Not Specified")

def run_integration_tests():
    """Run integration tests with detailed output."""
    print("Running Integration Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
    
    # Run tests with custom runner
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_integration_tests() 