#!/usr/bin/env python3
"""
Legal Contract Analysis - Main Orchestration Script
"""

import os
import sys
from typing import List, Dict, Any
from config.settings import SEARCH_TERMS, PROCESSING_PATH
from core.file_manager import FileManager
from core.llm_client import create_ollama_client
from core.excel_generator import ExcelGenerator
from utils.logger import logger

class LegalAnalyzer:
    """Main orchestrator for legal contract analysis"""
    
    def __init__(self):
        self.logger = logger
        self.file_manager = FileManager()
        self.llm_client = create_ollama_client()
        self.excel_generator = ExcelGenerator()
        
        # Track processing statistics
        self.total_companies = 0
        self.successful_companies = 0
        self.failed_companies = 0
    
    def run_analysis(self) -> bool:
        """Run the complete legal analysis workflow"""
        try:
            self.logger.info("🚀 Starting Legal Contract Analysis")
            self.logger.info("=" * 60)
            
            # Validate path structure
            if not self.file_manager.validate_path_structure():
                self.logger.error("❌ Path validation failed. Please check your PROCESSING_PATH in .env")
                return False
            
            # Test Ollama connection
            if not self.llm_client.test_connection():
                self.logger.error("❌ Cannot connect to Ollama. Please ensure Ollama is running.")
                return False
            
            # Get companies to process
            companies = self.file_manager.get_all_companies()
            
            if not companies:
                self.logger.error("❌ No companies found to process")
                return False
            
            self.total_companies = len(companies)
            self.logger.info(f"📊 Found {self.total_companies} companies to process")
            
            # Create blank Excel spreadsheet
            try:
                excel_filepath = self.excel_generator.create_blank_spreadsheet()
                self.logger.info(f"📊 Created blank Excel spreadsheet: {excel_filepath}")
            except Exception as e:
                self.logger.error(f"❌ Failed to create Excel spreadsheet: {e}")
                return False
            
            # Process each company sequentially
            for index, company in enumerate(companies, 1):
                self._process_company(company, index, excel_filepath)
            
            # Log final summary
            self._log_final_summary()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Analysis failed: {e}")
            return False
    
    def _process_company(self, company: Dict[str, str], index: int, excel_filepath: str):
        """Process a single company"""
        company_name = company['name']
        company_path = company['path']
        
        try:
            self.logger.info(f"📋 Processing {company_name} ({index}/{self.total_companies})")
            
            # Get combined text from all documents
            text_result = self.file_manager.get_company_combined_text(company_path)
            
            if not text_result or not text_result.get('combined_text'):
                self.logger.error(f"❌ No text content available for {company_name}")
                self.failed_companies += 1
                return
            
            # Prepare company data for LLM
            company_data = {
                'company_name': company_name,
                'combined_text': text_result['combined_text'],
                'search_terms': SEARCH_TERMS
            }
            
            # Send to Ollama for analysis
            analysis_result = self.llm_client.analyze_company_documents(company_data)
            
            if not analysis_result:
                self.logger.error(f"❌ LLM analysis failed for {company_name}")
                self.failed_companies += 1
                return
            
            # Add row to Excel
            try:
                self.excel_generator.add_company_row(excel_filepath, analysis_result, index + 1)
                self.successful_companies += 1
                self.logger.info(f"✅ Successfully processed {company_name}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to add {company_name} to Excel: {e}")
                self.failed_companies += 1
            
        except Exception as e:
            self.logger.error(f"❌ Processing error for {company_name}: {e}")
            self.failed_companies += 1
    
    def _log_final_summary(self):
        """Log the final processing summary"""
        self.logger.info("=" * 60)
        self.logger.info("📊 FINAL SUMMARY")
        self.logger.info(f"Total companies: {self.total_companies}")
        self.logger.info(f"Successful: {self.successful_companies}")
        self.logger.info(f"Failed: {self.failed_companies}")
        self.logger.info("=" * 60)

def main():
    """Main entry point"""
    analyzer = LegalAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("\n✅ Analysis completed successfully!")
    else:
        print("\n❌ Analysis failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
