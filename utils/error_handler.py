import os
from typing import Dict, Any, Optional
from utils.logger import logger
from core.summary_generator import SummaryGenerator
from config.settings import OUTPUT_DIR

class ErrorHandler:
    """Handle errors and create placeholder summaries for failed companies"""
    
    def __init__(self):
        self.logger = logger
        self.summary_generator = SummaryGenerator()
    
    def handle_processing_error(self, error_context: Dict[str, Any]) -> bool:
        """
        Handle errors during company processing
        
        Args:
            error_context: Dictionary containing error information
                - company_name: Name of the company
                - step: Processing step that failed
                - error: Error message
                - failed_documents: List of failed documents (optional)
                - document_stats: Document processing stats (optional)
        
        Returns:
            True if error was handled successfully, False otherwise
        """
        try:
            company_name = error_context.get('company_name', 'Unknown Company')
            step = error_context.get('step', 'Unknown Step')
            error_message = error_context.get('error', 'Unknown Error')
            failed_documents = error_context.get('failed_documents', [])
            document_stats = error_context.get('document_stats', {})
            
            self.logger.error(f"❌ Processing error for {company_name} at step '{step}': {error_message}")
            
            # Create error summary
            error_summary = self._create_error_summary_content(
                company_name, step, error_message, failed_documents, document_stats
            )
            
            # Generate placeholder PDF
            try:
                pdf_path = self.summary_generator.create_summary_pdf(error_summary)
                self.logger.info(f"✅ Error summary created for {company_name}: {pdf_path}")
                return True
            except Exception as e:
                self.logger.error(f"❌ Failed to create error summary for {company_name}: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error handler failed: {e}")
            return False
    
    def _create_error_summary_content(self, company_name: str, step: str, error_message: str, 
                                    failed_documents: list, document_stats: dict) -> Dict[str, Any]:
        """
        Create content for error summary
        
        Args:
            company_name: Name of the company
            step: Processing step that failed
            error_message: Error message
            failed_documents: List of failed documents
            document_stats: Document processing statistics
        
        Returns:
            Dictionary with error summary content
        """
        return {
            "company": f"{company_name} (PROCESSING FAILED)",
            "key_findings": [
                f"Processing failed at step: {step}",
                f"Error: {error_message}",
                "No analysis could be completed due to processing error"
            ],
            "risk_assessment": [
                "Unable to assess risks - processing failed",
                "Manual review of documents required",
                "Consider re-running analysis after resolving issues"
            ],
            "recommendations": [
                "Review the error message above",
                "Check if all documents are accessible and readable",
                "Verify Ollama is running and accessible",
                "Consider processing documents manually if issues persist"
            ],
            "document_stats": document_stats,
            "failed_documents": failed_documents,
            "raw_response": f"Processing failed at step '{step}' with error: {error_message}"
        }
    
    def create_error_summary(self, company_name: str, error_message: str, 
                           failed_documents: list = None) -> Optional[str]:
        """
        Create a simple error summary for a failed company
        
        Args:
            company_name: Name of the company
            error_message: Error message
            failed_documents: List of failed documents (optional)
        
        Returns:
            Path to the created error summary PDF, or None if failed
        """
        try:
            error_context = {
                'company_name': company_name,
                'step': 'General Processing',
                'error': error_message,
                'failed_documents': failed_documents or [],
                'document_stats': {'total': 0, 'successful': 0, 'failed': 0}
            }
            
            success = self.handle_processing_error(error_context)
            if success:
                # Return the expected path
                filename = f"{company_name} summary (ERROR).pdf"
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                return os.path.join(OUTPUT_DIR, filename)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create error summary for {company_name}: {e}")
            return None
    
    def validate_company_processing(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that a company has the minimum required data for processing
        
        Args:
            company_data: Company data to validate
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check required fields
            if not company_data.get('company_name'):
                validation['is_valid'] = False
                validation['errors'].append("Missing company name")
            
            if not company_data.get('combined_text'):
                validation['is_valid'] = False
                validation['errors'].append("No text content available for analysis")
            
            # Check document stats
            document_stats = company_data.get('document_stats', {})
            if document_stats.get('total', 0) == 0:
                validation['is_valid'] = False
                validation['errors'].append("No documents found in company folder")
            
            # Check for failed documents
            failed_documents = company_data.get('failed_documents', [])
            if failed_documents:
                validation['warnings'].append(f"{len(failed_documents)} documents failed to process")
            
            # Check if we have any successful documents
            if document_stats.get('successful', 0) == 0:
                validation['is_valid'] = False
                validation['errors'].append("No documents could be processed successfully")
            
            return validation
            
        except Exception as e:
            validation['is_valid'] = False
            validation['errors'].append(f"Validation error: {e}")
            return validation
    
    def log_processing_summary(self, total_companies: int, successful_companies: int, 
                             failed_companies: int, failed_company_details: list):
        """
        Log a summary of the entire processing run
        
        Args:
            total_companies: Total number of companies processed
            successful_companies: Number of successfully processed companies
            failed_companies: Number of failed companies
            failed_company_details: List of failed company details
        """
        try:
            self.logger.info("=" * 60)
            self.logger.info("PROCESSING SUMMARY")
            self.logger.info("=" * 60)
            self.logger.info(f"Total companies processed: {total_companies}")
            self.logger.info(f"Successfully processed: {successful_companies}")
            self.logger.info(f"Failed to process: {failed_companies}")
            
            if failed_companies > 0:
                self.logger.info("")
                self.logger.info("Failed companies:")
                for company_detail in failed_company_details:
                    self.logger.info(f"  - {company_detail['name']}: {company_detail['error']}")
            
            success_rate = (successful_companies / total_companies * 100) if total_companies > 0 else 0
            self.logger.info("")
            self.logger.info(f"Success rate: {success_rate:.1f}%")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log processing summary: {e}")
