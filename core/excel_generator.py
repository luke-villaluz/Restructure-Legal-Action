import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill
from typing import List, Dict, Any
from config.settings import OUTPUT_DIR
from utils.logger import logger

class ExcelGenerator:
    """Generate Excel spreadsheet with detailed contract analysis"""
    
    def __init__(self):
        self.logger = logger
        self.output_dir = OUTPUT_DIR
    
    def create_blank_spreadsheet(self) -> str:
        """Create a blank Excel spreadsheet with detailed headers"""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Contract Analysis"
            
            # Set up detailed headers
            self._setup_detailed_headers(ws)
            self._adjust_column_widths(ws)
            
            filename = "Contract_Name_Change_Analysis.xlsx"
            filepath = os.path.join(self.output_dir, filename)
            
            wb.save(filepath)
            self.logger.info(f"✅ Detailed Excel spreadsheet created: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create Excel spreadsheet: {e}")
            raise

    def add_company_row(self, excel_filepath: str, company_data: Dict[str, str], row_number: int):
        """Add a single company row to the existing Excel spreadsheet"""
        try:
            wb = load_workbook(excel_filepath)
            ws = wb.active
            
            # FIXED field mappings to match JSON response structure
            ws[f'A{row_number}'] = company_data.get('company', 'Unknown')
            ws[f'B{row_number}'] = company_data.get('contract_name', 'Not Specified')
            ws[f'C{row_number}'] = company_data.get('contract_counterparty', 'Not Specified')
            ws[f'D{row_number}'] = company_data.get('effective_date', 'Not Specified')
            ws[f'E{row_number}'] = company_data.get('renewal_termination_date', 'Not Specified')
            ws[f'F{row_number}'] = company_data.get('name_change_requires_notification', 'Not Specified')
            ws[f'G{row_number}'] = company_data.get('clause_reference', 'N/A')
            ws[f'H{row_number}'] = company_data.get('is_assignment', 'Not Specified')
            ws[f'I{row_number}'] = company_data.get('assignment_clause_reference', 'N/A')
            ws[f'J{row_number}'] = company_data.get('material_corporate_structure_clauses', 'Not Specified')
            ws[f'K{row_number}'] = company_data.get('notices_clause_present', 'Not Specified')
            ws[f'L{row_number}'] = company_data.get('action_required', 'Not Specified')
            ws[f'M{row_number}'] = company_data.get('recommended_action', 'Not Specified')
            
            # Format the row
            for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']:
                ws[f'{col}{row_number}'].alignment = Alignment(wrap_text=True, vertical="top")
            
            wb.save(excel_filepath)
            self.logger.info(f"✅ Added detailed row {row_number} for {company_data.get('company')}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add company row: {e}")
            raise

    def _setup_detailed_headers(self, ws):
        """Set up the detailed header row with formatting"""
        headers = [
            "Company",
            "Contract Name",
            "Contract Counterparty",
            "Effective Date",
            "Renewal/Termination Date",
            "Corporate Restructure or Name Change Requires Notification or Consent?",
            "Clause Reference (if Yes)",
            "Is a Corporate Restructure or a Name Change Considered an Assignment?",
            "Assignment Clause Reference (if Yes)",
            "Material Corporate Structure Change or Name Change Clauses?",
            "Notices Clause Present?",
            "Action Required Prior to Name Change or Corporate Restructure",
            "Recommended Action"
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    def _adjust_column_widths(self, ws):
        """Auto-adjust column widths for better readability"""
        column_widths = [20, 25, 25, 15, 20, 35, 30, 35, 30, 35, 25, 35, 25]
        
        for col, width in enumerate(column_widths, 1):
            ws.column_dimensions[chr(64 + col)].width = width