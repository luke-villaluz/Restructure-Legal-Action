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
            
            # Add data for each column
            ws[f'A{row_number}'] = company_data.get('company', 'Unknown')
            ws[f'B{row_number}'] = company_data.get('name_change_requires_notification', 'Not Specified')
            ws[f'C{row_number}'] = company_data.get('name_change_assignment', 'Unclear')
            ws[f'D{row_number}'] = company_data.get('assignment_clause_reference', '')
            ws[f'E{row_number}'] = company_data.get('material_corporate_structure', 'No')
            ws[f'F{row_number}'] = company_data.get('notices_clause_present', 'No')
            ws[f'G{row_number}'] = company_data.get('action_required', 'No Action Required')
            ws[f'H{row_number}'] = company_data.get('recommended_action', 'No Action')
            
            # Format the row
            for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
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
            "Name Change Requires Notification",
            "Is Name Change Considered an Assignment?",
            "Assignment Clause Reference (if Yes)",
            "Does the Contract Require Notification for Changes to Corporate Status?",
            "Notices Clause Present?",
            "Action Required Prior to Name Change",
            "Recommended Action"
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    def _adjust_column_widths(self, ws):
        """Auto-adjust column widths for better readability"""
        column_widths = [25, 30, 30, 30, 35, 25, 35, 25]  # Reduced width for "Name Change Requires Notification"
        
        for col, width in enumerate(column_widths, 1):
            ws.column_dimensions[chr(64 + col)].width = width