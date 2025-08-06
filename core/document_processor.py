"""Process PDF and Word documents for text extraction with OCR fallback."""

import os
import io
from typing import List, Dict, Optional, Any
from utils.logger import logger
from config.settings import TESSERACT_PATH

# Import OCR dependencies at module level
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import fitz  # PyMuPDF for PDF to image conversion
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class DocumentProcessor:
    """Process PDF and Word documents for text extraction with OCR fallback."""
    
    def __init__(self):
        self.logger = logger
        self.supported_extensions = ['.pdf', '.docx', '.doc']
        
    def is_document_file(self, filename: str) -> bool:
        """Check if file is a supported document type."""
        return any(filename.lower().endswith(ext) for ext in self.supported_extensions)
    
    def get_all_documents_in_folder(self, folder_path: str) -> List[str]:
        """Get all document files in a folder (including nested subfolders)."""
        document_files = []
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                if self.is_document_file(file):
                    full_path = os.path.join(root, file)
                    document_files.append(full_path)
                    self.logger.info(f"Found document: {full_path}")
        
        self.logger.info(f"Found {len(document_files)} documents in {folder_path}")
        return document_files
    
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract text from a PDF file using Tesseract OCR."""
        if not OCR_AVAILABLE:
            self.logger.error("OCR dependencies not installed. Install with: pip install pytesseract Pillow PyMuPDF")
            return None
            
        self.logger.info(f"Extracting text from: {pdf_path}")
        
        ocr_text = self._extract_text_with_tesseract(pdf_path)
        if ocr_text:
            self.logger.info(f"Successfully extracted {len(ocr_text)} characters from PDF using Tesseract OCR")
            return ocr_text
        
        self.logger.error(f"Failed to extract text from PDF: {pdf_path}")
        return None
    
    def _extract_text_with_tesseract(self, pdf_path: str) -> Optional[str]:
        """Extract text from PDF using Tesseract OCR."""
        if not os.path.exists(pdf_path):
            self.logger.error(f"PDF file does not exist: {pdf_path}")
            return None
            
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        self.logger.info(f"Starting Tesseract OCR processing for: {pdf_path}")
        
        try:
            pdf_document = fitz.open(pdf_path)
            extracted_text = ""
            
            for page_num in range(len(pdf_document)):
                page_text = self._process_single_page(pdf_document, page_num)
                if page_text:
                    extracted_text += page_text + "\n"
            
            pdf_document.close()
            return extracted_text.strip() if extracted_text.strip() else None
            
        except Exception as e:
            self.logger.error(f"Tesseract processing failed: {e}")
            return None
    
    def _process_single_page(self, pdf_document, page_num: int) -> Optional[str]:
        """Process a single PDF page with OCR."""
        try:
            page = pdf_document.load_page(page_num)
            mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for better OCR
            pix = page.get_pixmap(matrix=mat)
            
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Enhance image for better OCR
            img = self._enhance_image_for_ocr(img)
            
            # Perform OCR
            custom_config = r'--oem 3 --psm 6'
            page_text = pytesseract.image_to_string(img, config=custom_config, lang='eng')
            
            if page_text.strip():
                self.logger.info(f"Tesseract extracted {len(page_text)} characters from page {page_num + 1}")
                return page_text.strip()
            else:
                self.logger.warning(f"Tesseract found no text on page {page_num + 1}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Tesseract failed on page {page_num + 1}: {e}")
            return None
    
    def _enhance_image_for_ocr(self, img):
        """Enhance image for better OCR results."""
        if img.mode != 'L':
            img = img.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        # Apply slight blur to reduce noise
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return img
    
    def extract_text_from_word(self, word_path: str) -> Optional[str]:
        """Extract text from a Word document (.docx and .doc)."""
        self.logger.info(f"Extracting text from Word document: {word_path}")
        
        if word_path.lower().endswith('.docx'):
            return self._extract_from_docx(word_path)
        elif word_path.lower().endswith('.doc'):
            return self._extract_from_doc(word_path)
        else:
            self.logger.error(f"Unsupported Word format: {word_path}")
            return None
    
    def _extract_from_docx(self, word_path: str) -> Optional[str]:
        """Extract text from .docx file."""
        try:
            from docx import Document
            doc = Document(word_path)
            
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text.strip() + "\n"
            
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text += cell.text.strip() + "\n"
            
            if text.strip():
                self.logger.info(f"Successfully extracted {len(text)} characters from Word document (.docx)")
                return text.strip()
            
            self.logger.warning(f"No text extracted from Word document: {word_path}")
            return None
            
        except ImportError:
            self.logger.error("python-docx not installed. Install with: pip install python-docx")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting from .docx: {e}")
            return None
    
    def _extract_from_doc(self, word_path: str) -> Optional[str]:
        """Extract text from .doc file."""
        try:
            import win32com.client
            import pythoncom
            
            pythoncom.CoInitialize()
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            
            try:
                doc = word.Documents.Open(os.path.abspath(word_path))
                text = doc.Content.Text
                doc.Close()
                
                if text.strip():
                    self.logger.info(f"Successfully extracted {len(text)} characters from Word document (.doc)")
                    return text.strip()
                
                self.logger.warning(f"No text extracted from Word document: {word_path}")
                return None
                
            finally:
                word.Quit()
                pythoncom.CoUninitialize()
                
        except ImportError:
            self.logger.error("pywin32 not installed. Install with: pip install pywin32")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting from .doc: {e}")
            return None
    
    def extract_text_from_document(self, document_path: str) -> Optional[str]:
        """Extract text from any supported document type."""
        if document_path.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(document_path)
        elif document_path.lower().endswith(('.docx', '.doc')):
            return self.extract_text_from_word(document_path)
        else:
            self.logger.error(f"Unsupported document type: {document_path}")
            return None
    
    def extract_all_text_from_folder(self, folder_path: str) -> Dict[str, Any]:
        """Extract text from all documents in a folder."""
        document_files = self.get_all_documents_in_folder(folder_path)
        
        if not document_files:
            self.logger.warning(f"No documents found in {folder_path}")
            return self._empty_extraction_result()
        
        successful_texts = {}
        failed_documents = []
        
        for doc_path in document_files:
            text = self.extract_text_from_document(doc_path)
            if text:
                successful_texts[doc_path] = text
            else:
                failed_documents.append(os.path.basename(doc_path))
                self.logger.warning(f"Failed to extract text from {doc_path}")
        
        document_stats = {
            'total': len(document_files),
            'successful': len(successful_texts),
            'failed': len(failed_documents)
        }
        
        self.logger.info(f"Successfully extracted text from {len(successful_texts)} documents in {folder_path}")
        self.logger.info(f"Document stats: {document_stats}")
        
        return {
            'successful_texts': successful_texts,
            'failed_documents': failed_documents,
            'document_stats': document_stats
        }
    
    def combine_document_texts(self, document_texts: Dict[str, str]) -> str:
        """Combine text from multiple documents into a single analysis-ready text."""
        if not document_texts:
            return ""
        
        combined_text = ""
        for doc_path, text in document_texts.items():
            doc_name = os.path.basename(doc_path)
            combined_text += f"\n\n=== DOCUMENT: {doc_name} ===\n\n"
            combined_text += text
            combined_text += "\n\n"
        
        self.logger.info(f"Combined text from {len(document_texts)} documents ({len(combined_text)} total characters)")
        return combined_text.strip()
    
    def _empty_extraction_result(self) -> Dict[str, Any]:
        """Return empty extraction result structure."""
        return {
            'successful_texts': {},
            'failed_documents': [],
            'document_stats': {'total': 0, 'successful': 0, 'failed': 0}
        }