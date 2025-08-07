#!/usr/bin/env python3
"""
Legal Contract Analysis - Main Orchestration Script
"""

import os
import sys
from typing import List, Dict, Any, Optional
from config.settings import SEARCH_TERMS, PROCESSING_PATH
from core.file_manager import FileManager
from core.ai_factory import create_ai_client
from core.excel_generator import ExcelGenerator
from utils.logger import logger

class LegalAnalyzer:
    """Main orchestrator for legal contract analysis."""
    
    def __init__(self):
        self.logger = logger
        self.file_manager = FileManager()
        self.llm_client = create_ai_client(os.getenv('AI_PROVIDER', 'perplexity'))
        self.excel_generator = ExcelGenerator()
        
        # Track processing statistics
        self.total_companies = 0
        self.successful_companies = 0
        self.failed_companies = 0
        
        # NEW: Track all failed files
        self.failed_files = []
    
    def run_analysis(self) -> bool:
        """Run the complete legal analysis workflow."""
        self.logger.info("Starting Legal Contract Analysis")
        self.logger.info("=" * 60)
        
        # Validate setup
        if not self._validate_setup():
            return False
        
        # Get companies to process
        companies = self.file_manager.get_all_companies()
        if not companies:
            self.logger.error("No companies found to process")
            return False
        
        self.total_companies = len(companies)
        self.logger.info(f"Found {self.total_companies} companies to process")
        
        # Create Excel spreadsheet
        excel_filepath = self._create_excel_spreadsheet()
        if not excel_filepath:
            return False
        
        # Process each company
        for index, company in enumerate(companies, 1):
            self._process_company(company, index, excel_filepath)
        
        self._log_final_summary()
        self._print_failed_files_summary()  # NEW
        return True
    
    def _validate_setup(self) -> bool:
        """Validate path structure and AI connection."""
        if not self.file_manager.validate_path_structure():
            self.logger.error("Path validation failed. Please check your PROCESSING_PATH in .env")
            return False
        
        if not self.llm_client.test_connection():
            self.logger.error("Cannot connect to AI service. Please check your configuration.")
            return False
        
        return True
    
    def _create_excel_spreadsheet(self) -> Optional[str]:
        """Create blank Excel spreadsheet."""
        try:
            excel_filepath = self.excel_generator.create_blank_spreadsheet()
            self.logger.info(f"Created blank Excel spreadsheet: {excel_filepath}")
            return excel_filepath
        except Exception as e:
            self.logger.error(f"Failed to create Excel spreadsheet: {e}")
            return None
    
    def _process_company(self, company: Dict[str, str], index: int, excel_filepath: str):
        """Process a single company."""
        company_name = company['name']
        company_path = company['path']
        
        self.logger.info(f"Processing {company_name} ({index}/{self.total_companies})")
        
        # Get combined text from all documents
        text_result = self.file_manager.get_company_combined_text(company_path)
        if not text_result or not text_result.get('combined_text'):
            self.logger.error(f"No text content available for {company_name}")
            self.failed_companies += 1
            # NEW: Add failed files from this company
            self._add_failed_files_from_company(company_path, text_result)
            return
        
        # Prepare company data for LLM
        company_data = {
            'company_name': company_name,
            'combined_text': text_result['combined_text'],
            'search_terms': SEARCH_TERMS
        }
        
        # Send to LLM for analysis
        analysis_result = self.llm_client.analyze_company_documents(company_data)
        if not analysis_result:
            self.logger.error(f"LLM analysis failed for {company_name}")
            self.failed_companies += 1
            return
        
        # Add row to Excel
        if self._add_to_excel(excel_filepath, analysis_result, index + 1):
            self.successful_companies += 1
            self.logger.info(f"Successfully processed {company_name}")
        else:
            self.failed_companies += 1
    
    def _add_to_excel(self, excel_filepath: str, analysis_result: Dict[str, Any], row_number: int) -> bool:
        """Add company data to Excel spreadsheet."""
        try:
            self.excel_generator.add_company_row(excel_filepath, analysis_result, row_number)
            return True
        except Exception as e:
            self.logger.error(f"Failed to add to Excel: {e}")
            return False
    
    def _log_final_summary(self):
        """Log the final processing summary."""
        self.logger.info("=" * 60)
        self.logger.info("FINAL SUMMARY")
        self.logger.info(f"Total companies: {self.total_companies}")
        self.logger.info(f"Successful: {self.successful_companies}")
        self.logger.info(f"Failed: {self.failed_companies}")
        self.logger.info("=" * 60)

    def _add_failed_files_from_company(self, company_path: str, text_result: Dict[str, Any]):
        """Add failed files from a company to the failure list."""
        if text_result and 'failed_documents' in text_result:
            for failed_doc in text_result['failed_documents']:
                # Get the full path of the failed document
                full_path = os.path.join(company_path, failed_doc)
                self.failed_files.append({
                    'file_path': full_path,
                    'company': os.path.basename(company_path),
                    'reason': 'Text extraction failed'
                })
    
    def _print_failed_files_summary(self):
        """Print a comprehensive summary of all failed files."""
        if not self.failed_files:
            self.logger.info("No files failed to process!")
            return
        
        self.logger.info("=" * 80)
        self.logger.info("FAILED FILES SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Total failed files: {len(self.failed_files)}")
        self.logger.info("")
        
        # Group by company
        failed_by_company = {}
        for failed_file in self.failed_files:
            company = failed_file['company']
            if company not in failed_by_company:
                failed_by_company[company] = []
            failed_by_company[company].append(failed_file)
        
        # Print by company
        for company, files in failed_by_company.items():
            self.logger.info(f"COMPANY: {company}")
            self.logger.info(f"Failed files: {len(files)}")
            for failed_file in files:
                self.logger.info(f"  - {failed_file['file_path']}")
                self.logger.info(f"    Reason: {failed_file['reason']}")
            self.logger.info("")
        
        # Print complete list
        self.logger.info("COMPLETE LIST OF FAILED FILES:")
        self.logger.info("-" * 80)
        for failed_file in self.failed_files:
            self.logger.info(failed_file['file_path'])
        
        self.logger.info("=" * 80)

def main():
    """Main entry point."""
    analyzer = LegalAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("\nAnalysis completed successfully!")
    else:
        print("\nAnalysis failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
