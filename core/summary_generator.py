import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, darkblue, darkred, darkgreen
from config.settings import OUTPUT_DIR
from utils.logger import logger

class SummaryGenerator:
    """Generate PDF summaries from contract analysis results"""
    
    def __init__(self):
        self.logger = logger
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the summary"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=darkblue,
            alignment=1  # Center alignment
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=darkblue
        )
        
        # Finding item style
        self.finding_style = ParagraphStyle(
            'CustomFinding',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20,
            bulletIndent=10,
            bulletText='•'
        )
        
        # Risk item style
        self.risk_style = ParagraphStyle(
            'CustomRisk',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20,
            bulletIndent=10,
            bulletText='⚠',
            textColor=darkred
        )
        
        # Recommendation style
        self.recommendation_style = ParagraphStyle(
            'CustomRecommendation',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20,
            bulletIndent=10,
            bulletText='→',
            textColor=darkgreen
        )
    
    def create_summary_pdf(self, analysis_data: dict) -> str:
        """
        Create a PDF summary from analysis data
        
        Args:
            analysis_data: Dictionary containing analysis results
                - company: Company name
                - key_findings: List of key findings
                - risk_assessment: List of risk assessments
                - recommendations: List of recommendations
                - document_stats: Document processing statistics (optional)
                - failed_documents: List of failed documents (optional)
                - raw_response: Raw AI response (optional)
        
        Returns:
            Path to the created PDF file
        """
        try:
            company_name = analysis_data.get('company', 'Unknown Company')
            
            # Create output directory if it doesn't exist
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Generate filename
            filename = f"{company_name} summary.pdf"
            # Clean filename for filesystem compatibility
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            self.logger.info(f"📄 Creating summary PDF for {company_name}")
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []
            
            # Add title
            title = Paragraph(f"Contract Analysis Summary<br/>{company_name}", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Add key findings section
            if analysis_data.get('key_findings'):
                story.append(Paragraph("Key Findings", self.section_style))
                for finding in analysis_data['key_findings']:
                    story.append(Paragraph(finding, self.finding_style))
                story.append(Spacer(1, 12))
            
            # Add risk assessment section
            if analysis_data.get('risk_assessment'):
                story.append(Paragraph("Risk Assessment", self.section_style))
                for risk in analysis_data['risk_assessment']:
                    story.append(Paragraph(risk, self.risk_style))
                story.append(Spacer(1, 12))
            
            # Add recommendations section
            if analysis_data.get('recommendations'):
                story.append(Paragraph("Recommendations", self.section_style))
                for recommendation in analysis_data['recommendations']:
                    story.append(Paragraph(recommendation, self.recommendation_style))
                story.append(Spacer(1, 12))
            
            # Add document processing summary section (if metadata exists)
            document_stats = analysis_data.get('document_stats', {})
            failed_documents = analysis_data.get('failed_documents', [])
            
            if document_stats or failed_documents:
                story.append(Paragraph("Document Processing Summary", self.section_style))
                
                # Add processing statistics
                if document_stats:
                    total = document_stats.get('total', 0)
                    successful = document_stats.get('successful', 0)
                    failed = document_stats.get('failed', 0)
                    
                    story.append(Paragraph(f"Total documents processed: {total}", self.styles['Normal']))
                    story.append(Paragraph(f"Successfully processed: {successful} documents", self.styles['Normal']))
                    story.append(Paragraph(f"Failed to process: {failed} documents", self.styles['Normal']))
                    story.append(Spacer(1, 6))
                
                # Add failed documents list
                if failed_documents:
                    story.append(Paragraph("Documents requiring manual review:", self.styles['Normal']))
                    for failed_doc in failed_documents:
                        story.append(Paragraph(f"• {failed_doc}", self.styles['Normal']))
                    story.append(Spacer(1, 6))
            
            # Add raw response section (collapsed by default)
            if analysis_data.get('raw_response'):
                story.append(Paragraph("Full Analysis Response", self.section_style))
                raw_text = analysis_data['raw_response'][:1000] + "..." if len(analysis_data['raw_response']) > 1000 else analysis_data['raw_response']
                story.append(Paragraph(raw_text, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"✅ Summary PDF created: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create summary PDF for {company_name}: {e}")
            raise
    
    def create_placeholder_summary(self, company_name: str, error_message: str) -> str:
        """
        Create a placeholder summary when analysis fails
        
        Args:
            company_name: Name of the company
            error_message: Error message to include
        
        Returns:
            Path to the created PDF file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Generate filename
            filename = f"{company_name} summary (ERROR).pdf"
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []
            
            # Add title
            title = Paragraph(f"Contract Analysis Summary<br/>{company_name}<br/>(Analysis Failed)", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Add error message
            story.append(Paragraph("Analysis Error", self.section_style))
            story.append(Paragraph(f"Unable to analyze contract: {error_message}", self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            self.logger.warning(f"⚠️ Placeholder summary created for {company_name}: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create placeholder summary for {company_name}: {e}")
            raise
