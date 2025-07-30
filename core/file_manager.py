import os
from typing import List, Dict, Optional, Any
from config.settings import PROCESSING_PATH  # Changed from PATH to PROCESSING_PATH
from utils.logger import logger

class FileManager:
    """Manages file operations for the legal analysis workflow using a single path"""
    
    def __init__(self):
        self.logger = logger
        self.base_path = PROCESSING_PATH  # Changed from PATH to PROCESSING_PATH
        
    def get_all_companies(self) -> List[Dict[str, str]]:
        """
        Discover all company folders in the single path
        
        Returns:
            List of dictionaries with company info:
            {
                'name': 'Company Name',
                'type': 'company', 
                'path': 'full/path/to/company/folder'
            }
        """
        companies = []
        
        try:
            if not self.base_path or not os.path.exists(self.base_path):
                self.logger.error(f"❌ Base path not found: {self.base_path}")
                return []
            
            # Get all subfolders in the base path
            subfolders = [
                f for f in os.listdir(self.base_path) 
                if os.path.isdir(os.path.join(self.base_path, f))
            ]
            
            for folder in subfolders:
                companies.append({
                    'name': folder,
                    'type': 'company',
                    'path': os.path.join(self.base_path, folder)
                })
            
            self.logger.info(f"📁 Found {len(companies)} companies in {self.base_path}")
            return companies
            
        except Exception as e:
            self.logger.error(f"❌ Error discovering companies: {e}")
            return []
    
    def get_company_documents(self, company_folder_path: str) -> List[str]:
        """
        Get all document files in a company folder (including nested subfolders)
        
        Args:
            company_folder_path: Path to the company's folder
            
        Returns:
            List of full paths to all document files
        """
        try:
            if not os.path.exists(company_folder_path):
                self.logger.error(f"❌ Company folder does not exist: {company_folder_path}")
                return []
            
            # Import here to avoid circular imports
            from core.document_processor import DocumentProcessor
            processor = DocumentProcessor()
            
            # Get all documents in the company folder
            document_files = processor.get_all_documents_in_folder(company_folder_path)
            
            if len(document_files) == 0:
                self.logger.warning(f"⚠️ No documents found in {company_folder_path}")
            else:
                self.logger.info(f"✅ Found {len(document_files)} documents in {company_folder_path}")
            
            return document_files
            
        except Exception as e:
            self.logger.error(f"❌ Error getting documents for {company_folder_path}: {e}")
            return []
    
    def get_company_combined_text(self, company_folder_path: str) -> Dict[str, Any]:
        """
        Get combined text from all documents in a company folder
        
        Args:
            company_folder_path: Path to the company's folder
            
        Returns:
            Dictionary containing:
            {
                'combined_text': str,                    # Combined text from all documents
                'document_stats': Dict[str, int],        # total, successful, failed counts
                'failed_documents': List[str]            # List of failed document names
            }
        """
        try:
            if not os.path.exists(company_folder_path):
                self.logger.error(f"❌ Company folder does not exist: {company_folder_path}")
                return {
                    'combined_text': "",
                    'document_stats': {'total': 0, 'successful': 0, 'failed': 0},
                    'failed_documents': []
                }
            
            # Import here to avoid circular imports
            from core.document_processor import DocumentProcessor
            processor = DocumentProcessor()
            
            # Extract text from all documents with metadata
            extraction_results = processor.extract_all_text_from_folder(company_folder_path)
            
            if not extraction_results['successful_texts']:
                self.logger.warning(f"⚠️ No text extracted from {company_folder_path}")
                return {
                    'combined_text': "",
                    'document_stats': extraction_results['document_stats'],
                    'failed_documents': extraction_results['failed_documents']
                }
            
            # Combine all successful text
            combined_text = processor.combine_document_texts(extraction_results['successful_texts'])
            
            if combined_text:
                self.logger.info(f"✅ Successfully combined text from {len(extraction_results['successful_texts'])} documents ({len(combined_text)} characters)")
                return {
                    'combined_text': combined_text,
                    'document_stats': extraction_results['document_stats'],
                    'failed_documents': extraction_results['failed_documents']
                }
            else:
                self.logger.warning(f"⚠️ Failed to combine text from {company_folder_path}")
                return {
                    'combined_text': "",
                    'document_stats': extraction_results['document_stats'],
                    'failed_documents': extraction_results['failed_documents']
                }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting combined text for {company_folder_path}: {e}")
            return {
                'combined_text': "",
                'document_stats': {'total': 0, 'successful': 0, 'failed': 0},
                'failed_documents': []
            }
    
    def validate_path_structure(self) -> bool:
        """
        Validate that the base path exists and has content
        
        Returns:
            True if valid, False otherwise
        """
        try:
            if not self.base_path:
                self.logger.error("❌ PROCESSING_PATH not set in .env file")
                return False
            
            if not os.path.exists(self.base_path):
                self.logger.error(f"❌ Path does not exist: {self.base_path}")
                return False
            
            companies = self.get_all_companies()
            if not companies:
                self.logger.error(f"❌ No company folders found in {self.base_path}")
                return False
            
            self.logger.info(f"✅ Path validation successful: {len(companies)} companies found")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating path structure: {e}")
            return False
