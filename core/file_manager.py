"""Manage file operations for the legal analysis workflow."""

import os
from typing import List, Dict, Any
from config.settings import PROCESSING_PATH
from utils.logger import logger

class FileManager:
    """Manages file operations for the legal analysis workflow."""
    
    def __init__(self):
        self.logger = logger
        self.base_path = PROCESSING_PATH
        
    def get_all_companies(self) -> List[Dict[str, str]]:
        """Discover all company folders in the processing path."""
        if not self._validate_base_path():
            return []
        
        subfolders = [
            f for f in os.listdir(self.base_path) 
            if os.path.isdir(os.path.join(self.base_path, f))
        ]
        
        companies = [
            {
                'name': folder,
                'type': 'company',
                'path': os.path.join(self.base_path, folder)
            }
            for folder in subfolders
        ]
        
        self.logger.info(f"Found {len(companies)} companies in {self.base_path}")
        return companies
    
    def get_company_documents(self, company_folder_path: str) -> List[str]:
        """Get all document files in a company folder."""
        if not os.path.exists(company_folder_path):
            self.logger.error(f"Company folder does not exist: {company_folder_path}")
            return []
        
        from core.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        document_files = processor.get_all_documents_in_folder(company_folder_path)
        
        if not document_files:
            self.logger.warning(f"No documents found in {company_folder_path}")
        else:
            self.logger.info(f"Found {len(document_files)} documents in {company_folder_path}")
        
        return document_files
    
    def get_company_combined_text(self, company_folder_path: str) -> Dict[str, Any]:
        """Get combined text from all documents in a company folder."""
        if not os.path.exists(company_folder_path):
            self.logger.error(f"Company folder does not exist: {company_folder_path}")
            return self._empty_text_result()
        
        from core.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        extraction_results = processor.extract_all_text_from_folder(company_folder_path)
        
        if not extraction_results['successful_texts']:
            self.logger.warning(f"No text extracted from {company_folder_path}")
            return {
                'combined_text': "",
                'document_stats': extraction_results['document_stats'],
                'failed_documents': extraction_results['failed_documents']
            }
        
        combined_text = processor.combine_document_texts(extraction_results['successful_texts'])
        
        if combined_text:
            self.logger.info(f"Successfully combined text from {len(extraction_results['successful_texts'])} documents ({len(combined_text)} characters)")
            return {
                'combined_text': combined_text,
                'document_stats': extraction_results['document_stats'],
                'failed_documents': extraction_results['failed_documents']
            }
        
        self.logger.warning(f"Failed to combine text from {company_folder_path}")
        return {
            'combined_text': "",
            'document_stats': extraction_results['document_stats'],
            'failed_documents': extraction_results['failed_documents']
        }
    
    def validate_path_structure(self) -> bool:
        """Validate that the base path exists and has content."""
        if not self.base_path:
            self.logger.error("PROCESSING_PATH not set in .env file")
            return False
        
        if not os.path.exists(self.base_path):
            self.logger.error(f"Path does not exist: {self.base_path}")
            return False
        
        companies = self.get_all_companies()
        if not companies:
            self.logger.error(f"No company folders found in {self.base_path}")
            return False
        
        self.logger.info(f"Path validation successful: {len(companies)} companies found")
        return True
    
    def _validate_base_path(self) -> bool:
        """Validate base path exists."""
        if not self.base_path or not os.path.exists(self.base_path):
            self.logger.error(f"Base path not found: {self.base_path}")
            return False
        return True
    
    def _empty_text_result(self) -> Dict[str, Any]:
        """Return empty text result structure."""
        return {
            'combined_text': "",
            'document_stats': {'total': 0, 'successful': 0, 'failed': 0},
            'failed_documents': []
        }
