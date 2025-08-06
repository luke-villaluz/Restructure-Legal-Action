"""Test runner for all test suites."""

import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from test_document_processor import run_document_processor_tests
from test_perplexity import run_perplexity_tests
from test_integration import run_integration_tests

def run_all_tests():
    """Run all test suites and provide comprehensive summary."""
    print("Running Complete Test Suite")
    print("=" * 60)
    
    # Track results
    results = {}
    
    # Run document processor tests
    print("\n1. Document Processor Tests")
    print("-" * 30)
    results['document_processor'] = run_document_processor_tests()
    
    # Run Perplexity API tests
    print("\n2. Perplexity API Tests")
    print("-" * 30)
    results['perplexity'] = run_perplexity_tests()
    
    # Run integration tests
    print("\n3. Integration Tests")
    print("-" * 30)
    results['integration'] = run_integration_tests()
    
    # Print final summary
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_suite, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_suite.replace('_', ' ').title()}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED!")
        return True
    else:
        print("SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 