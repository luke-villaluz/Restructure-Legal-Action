#!/usr/bin/env python3
"""
Legal Contract Analysis - Main Orchestration Script
Processes all company folders and generates analysis summaries
"""

import os
import sys
from typing import List, Dict, Any
from config.settings import SEARCH_TERMS, MAIN_TEST_FOLDER_PATH
from core.file_manager import FileManager
from core.llm_client import create_ollama_client
from core.summary_generator import SummaryGenerator
from utils.error_handler import ErrorHandler
from utils.logger import logger

class LegalAnalyzer:
    """Main orchestrator for legal contract analysis"""
    
    def __init__(self):
        self.logger = logger
        self.file_manager = FileManager()
        self.llm_client = create_ollama_client()
        self.summary_generator = SummaryGenerator()
        self.error_handler = ErrorHandler()
        
        # Track processing statistics
        self.total_companies = 0
        self.successful_companies = 0
        self.failed_companies = 0
        self.failed_company_details = []
    
    def run_analysis(self) -> bool:
        """
        Run the complete legal analysis workflow
        
        Returns:
            True if analysis completed successfully, False otherwise
        """
        try:
            self.logger.info("🚀 Starting Legal Contract Analysis")
            self.logger.info("=" * 60)
            
            # Test Ollama connection
            if not self.llm_client.test_connection():
                self.logger.error("❌ Cannot connect to Ollama. Please ensure Ollama is running.")
                return False
            
            # Get companies to process from MAIN_TEST_FOLDER_PATH
            companies = self._get_companies_from_path()
            
            if not companies:
                self.logger.error("❌ No companies found to process")
                return False
            
            self.total_companies = len(companies)
            self.logger.info(f"📊 Found {self.total_companies} companies to process")
            
            # Process each company sequentially
            for index, company in enumerate(companies, 1):
                self._process_company(company, index)
            
            # Log final summary
            self._log_final_summary()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Analysis failed: {e}")
            return False
    
    def _get_companies_from_path(self) -> List[Dict[str, str]]:
        """Get companies from the path specified in MAIN_TEST_FOLDER_PATH"""
        try:
            if not MAIN_TEST_FOLDER_PATH or not os.path.exists(MAIN_TEST_FOLDER_PATH):
                self.logger.error(f"❌ Path not found: {MAIN_TEST_FOLDER_PATH}")
                self.logger.error("Please check your MAIN_TEST_FOLDER_PATH in .env")
                return []
            
            # Get all subfolders in the specified directory
            subfolders = [
                f for f in os.listdir(MAIN_TEST_FOLDER_PATH) 
                if os.path.isdir(os.path.join(MAIN_TEST_FOLDER_PATH, f))
            ]
            
            companies = []
            for folder in subfolders:
                companies.append({
                    'name': folder,
                    'type': 'company',
                    'path': os.path.join(MAIN_TEST_FOLDER_PATH, folder)
                })
            
            self.logger.info(f"📁 Processing companies from: {MAIN_TEST_FOLDER_PATH}")
            self.logger.info(f"Found {len(companies)} companies to process")
            return companies
            
        except Exception as e:
            self.logger.error(f"❌ Error getting companies from path: {e}")
            return []
    
    def _process_company(self, company: Dict[str, str], index: int):
        """Process a single company"""
        company_name = company['name']
        company_path = company['path']
        
        try:
            self.logger.info(f"📋 Processing {company_name} ({index}/{self.total_companies})")
            
            # Get combined text from all documents
            text_result = self.file_manager.get_company_combined_text(company_path)
            
            if not text_result or not text_result.get('combined_text'):
                self._handle_company_error(company_name, "No text content available", text_result)
                return
            
            # Validate company data
            company_data = {
                'company_name': company_name,
                'combined_text': text_result['combined_text'],
                'search_terms': SEARCH_TERMS,
                'document_stats': text_result.get('document_stats', {}),
                'failed_documents': text_result.get('failed_documents', [])
            }
            
            validation = self.error_handler.validate_company_processing(company_data)
            if not validation['is_valid']:
                error_msg = "; ".join(validation['errors'])
                self._handle_company_error(company_name, error_msg, text_result)
                return
            
            # Send to Ollama for analysis
            analysis_result = self.llm_client.analyze_company_documents(company_data)
            
            if not analysis_result:
                self._handle_company_error(company_name, "LLM analysis failed", text_result)
                return
            
            # Generate summary PDF
            try:
                pdf_path = self.summary_generator.create_summary_pdf(analysis_result)
                self.logger.info(f"✅ Summary created for {company_name}: {pdf_path}")
                self.successful_companies += 1
                
            except Exception as e:
                self._handle_company_error(company_name, f"Summary generation failed: {e}", text_result)
                return
            
        except Exception as e:
            self._handle_company_error(company_name, f"Processing error: {e}", {})
    
    def _handle_company_error(self, company_name: str, error_message: str, context_data: Dict[str, Any]):
        """Handle errors for a specific company"""
        self.logger.error(f"❌ Failed to process {company_name}: {error_message}")
        
        # Create error summary
        try:
            self.error_handler.handle_processing_error({
                'company_name': company_name,
                'step': 'Company Processing',
                'error': error_message,
                'failed_documents': context_data.get('failed_documents', []),
                'document_stats': context_data.get('document_stats', {})
            })
        except Exception as e:
            self.logger.error(f"❌ Failed to create error summary for {company_name}: {e}")
        
        # Track failure
        self.failed_companies += 1
        self.failed_company_details.append({
            'name': company_name,
            'error': error_message
        })
    
    def _log_final_summary(self):
        """Log the final processing summary"""
        self.error_handler.log_processing_summary(
            self.total_companies,
            self.successful_companies,
            self.failed_companies,
            self.failed_company_details
        )

def main():
    """Main entry point"""
    # Initialize analyzer
    analyzer = LegalAnalyzer()
    
    # Run analysis
    success = analyzer.run_analysis()
    
    if success:
        print("\n�� Analysis completed successfully!")
    else:
        print("\n❌ Analysis failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
