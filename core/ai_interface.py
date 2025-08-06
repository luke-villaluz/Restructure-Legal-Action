"""Abstract interface for AI analysis services."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AIAnalyzer(ABC):
    """Abstract interface for AI analysis services."""
    
    @abstractmethod
    def analyze_company_documents(self, company_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze company documents and return structured results."""
        pass
    
    @abstractmethod
    def _parse_detailed_response(self, text: str, company_name: str) -> Dict[str, Any]:
        """Parse AI response into structured format."""
        pass
