"""Test suite for Perplexity API integration."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import requests

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.perplexity_client import PerplexityClient
from dotenv import load_dotenv

load_dotenv()

class TestPerplexityClient(unittest.TestCase):
    """Test cases for PerplexityClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = PerplexityClient()
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
    
    def test_client_initialization(self):
        """Test PerplexityClient initialization."""
        self.assertIsNotNone(self.client.model)
        self.assertIsNotNone(self.client.base_url)
        self.assertEqual(self.client.api_key, self.api_key)
    
    @patch('requests.post')
    def test_successful_connection(self, mock_post):
        """Test successful API connection."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.client.test_connection()
        self.assertTrue(result)
    
    @patch('requests.post')
    def test_failed_connection(self, mock_post):
        """Test failed API connection."""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        result = self.client.test_connection()
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_connection_exception(self, mock_post):
        """Test connection with network exception."""
        # Mock network exception
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        result = self.client.test_connection()
        self.assertFalse(result)
    
    def test_analyze_company_documents_empty_text(self):
        """Test analysis with empty text."""
        company_data = {
            'company_name': 'Test Company',
            'combined_text': '',
            'search_terms': ['test']
        }
        
        result = self.client.analyze_company_documents(company_data)
        self.assertIsNone(result)
    
    def test_analyze_company_documents_missing_data(self):
        """Test analysis with missing company data."""
        company_data = {}
        
        result = self.client.analyze_company_documents(company_data)
        self.assertIsNone(result)

def run_perplexity_tests():
    """Run Perplexity API tests with detailed output."""
    print("Running Perplexity API Tests")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("PERPLEXITY_API_KEY not found in environment")
        print("Some tests will be skipped")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPerplexityClient)
    
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
    run_perplexity_tests()
