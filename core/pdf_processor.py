import os
import PyPDF2
import pdfplumber
from utils.logger import logger, log_error

class PDFProcessor:
    """Handles PDF file reading and text extraction."""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using multiple methods for better results.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            logger.info(f"Extracting text from: {pdf_path}")
            
            # Try pdfplumber first (better for complex layouts)
            text = self._extract_with_pdfplumber(pdf_path)
            
            # If pdfplumber fails or returns minimal text, try PyPDF2
            if not text or len(text.strip()) < 100:
                logger.info("pdfplumber returned minimal text, trying PyPDF2")
                text = self._extract_with_pypdf2(pdf_path)
            
            if not text:
                raise Exception("No text could be extracted from PDF")
            
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text
            
        except Exception as e:
            error_msg = f"Failed to extract text from {pdf_path}: {str(e)}"
            log_error(error_msg)
            raise
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber (better for complex layouts)."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
            return ""
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2 (fallback method)."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
            return ""
    
    def is_pdf_file(self, file_path: str) -> bool:
        """Check if a file is a PDF based on extension."""
        return os.path.splitext(file_path.lower())[1] in self.supported_extensions
    
    def get_pdf_files_in_directory(self, directory_path: str) -> list:
        """
        Get all PDF files in a directory.
        
        Args:
            directory_path (str): Path to directory to search
            
        Returns:
            list: List of PDF file paths
        """
        pdf_files = []
        try:
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if os.path.isfile(file_path) and self.is_pdf_file(file_path):
                    pdf_files.append(file_path)
            
            logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")
            return pdf_files
            
        except Exception as e:
            error_msg = f"Failed to scan directory {directory_path}: {str(e)}"
            log_error(error_msg)
            raise
