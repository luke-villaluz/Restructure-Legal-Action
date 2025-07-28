import os
from typing import List, Dict, Optional, Any
from config.settings import INPUT_DIRECTORY
from utils.logger import logger

class FileManager:
    """Manages file operations and company discovery for the legal analysis workflow"""
    
    def __init__(self):
        self.logger = logger
        self.vendors_path = "data/Vendors"
        self.clients_path = "data/Clients"
        
    def get_all_companies(self) -> List[Dict[str, str]]:
        """
        Discover all company folders in Vendors and Clients directories
        
        Returns:
            List of dictionaries with company info:
            {
                'name': 'Company Name',
                'type': 'vendor' or 'client', 
                'path': 'full/path/to/company/folder'
            }
        """
        companies = []
        
        try:
            # Scan Vendors
            if os.path.exists(self.vendors_path):
                vendor_folders = self._get_company_folders(self.vendors_path)
                for folder in vendor_folders:
                    companies.append({
                        'name': folder,
                        'type': 'vendor',
                        'path': os.path.join(self.vendors_path, folder)
                    })
                self.logger.info(f"Found {len(vendor_folders)} vendor companies")
            
            # Scan Clients
            if os.path.exists(self.clients_path):
                client_folders = self._get_company_folders(self.clients_path)
                for folder in client_folders:
                    companies.append({
                        'name': folder,
                        'type': 'client',
                        'path': os.path.join(self.clients_path, folder)
                    })
                self.logger.info(f"Found {len(client_folders)} client companies")
            
            total_companies = len(companies)
            self.logger.info(f"Total companies discovered: {total_companies}")
            
            return companies
            
        except Exception as e:
            self.logger.error(f"Error discovering companies: {e}")
            return []
    
    def _get_company_folders(self, directory_path: str) -> List[str]:
        """
        Get list of company folder names from a directory
        
        Args:
            directory_path: Path to Vendors or Clients directory
            
        Returns:
            List of company folder names
        """
        try:
            if not os.path.exists(directory_path):
                return []
            
            # Get all subdirectories (company folders)
            company_folders = [
                f for f in os.listdir(directory_path) 
                if os.path.isdir(os.path.join(directory_path, f))
            ]
            
            return company_folders
            
        except Exception as e:
            self.logger.error(f"Error getting company folders from {directory_path}: {e}")
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
                self.logger.error(f"Company folder does not exist: {company_folder_path}")
                return []
            
            # Import here to avoid circular imports
            from core.document_processor import DocumentProcessor
            processor = DocumentProcessor()
            
            # Get all documents in the company folder
            document_files = processor.get_all_documents_in_folder(company_folder_path)
            
            if len(document_files) == 0:
                self.logger.warning(f"No documents found in {company_folder_path}")
            else:
                self.logger.info(f"Found {len(document_files)} documents in {company_folder_path}")
            
            return document_files
            
        except Exception as e:
            self.logger.error(f"Error getting documents for {company_folder_path}: {e}")
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
                self.logger.error(f"Company folder does not exist: {company_folder_path}")
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
                self.logger.warning(f"No text extracted from {company_folder_path}")
                return {
                    'combined_text': "",
                    'document_stats': extraction_results['document_stats'],
                    'failed_documents': extraction_results['failed_documents']
                }
            
            # Combine all successful text
            combined_text = processor.combine_document_texts(extraction_results['successful_texts'])
            
            if combined_text:
                self.logger.info(f"Successfully combined text from {len(extraction_results['successful_texts'])} documents ({len(combined_text)} characters)")
                return {
                    'combined_text': combined_text,
                    'document_stats': extraction_results['document_stats'],
                    'failed_documents': extraction_results['failed_documents']
                }
            else:
                self.logger.warning(f"Failed to combine text from {company_folder_path}")
                return {
                    'combined_text': "",
                    'document_stats': extraction_results['document_stats'],
                    'failed_documents': extraction_results['failed_documents']
                }
            
        except Exception as e:
            self.logger.error(f"Error getting combined text for {company_folder_path}: {e}")
            return {
                'combined_text': "",
                'document_stats': {'total': 0, 'successful': 0, 'failed': 0},
                'failed_documents': []
            }
    
    def validate_company_structure(self) -> Dict[str, bool]:
        """
        Validate that the expected directory structure exists
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            'vendors_exists': False,
            'clients_exists': False,
            'vendors_has_folders': False,
            'clients_has_folders': False
        }
        
        try:
            # Check Vendors directory
            if os.path.exists(self.vendors_path):
                validation['vendors_exists'] = True
                vendor_folders = self._get_company_folders(self.vendors_path)
                validation['vendors_has_folders'] = len(vendor_folders) > 0
            
            # Check Clients directory
            if os.path.exists(self.clients_path):
                validation['clients_exists'] = True
                client_folders = self._get_company_folders(self.clients_path)
                validation['clients_has_folders'] = len(client_folders) > 0
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Error validating company structure: {e}")
            return validation
    
    def get_company_count(self) -> Dict[str, int]:
        """
        Get count of companies by type
        
        Returns:
            Dictionary with counts: {'vendors': X, 'clients': Y, 'total': Z}
        """
        try:
            companies = self.get_all_companies()
            
            vendor_count = len([c for c in companies if c['type'] == 'vendor'])
            client_count = len([c for c in companies if c['type'] == 'client'])
            total_count = len(companies)
            
            return {
                'vendors': vendor_count,
                'clients': client_count,
                'total': total_count
            }
            
        except Exception as e:
            self.logger.error(f"Error getting company count: {e}")
            return {'vendors': 0, 'clients': 0, 'total': 0}
