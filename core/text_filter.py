import re
from typing import List, Set
from utils.logger import logger

class TextFilter:
    """Filter text to only include sections near search terms"""
    
    def __init__(self, search_terms: List[str], window_size: int = 1000):
        self.search_terms = [term.lower() for term in search_terms]
        self.window_size = window_size
        self.logger = logger
    
    def filter_text(self, combined_text: str) -> str:
        """
        Filter text to only include sections within window_size words of search terms
        
        Args:
            combined_text: Full text from all documents
            
        Returns:
            Filtered text containing only relevant sections
        """
        try:
            if not combined_text or not self.search_terms:
                return combined_text
            
            # Split text into words
            words = combined_text.split()
            filtered_sections = []
            
            # Find positions of search terms
            term_positions = []
            for i, word in enumerate(words):
                word_lower = word.lower()
                for term in self.search_terms:
                    if term in word_lower:
                        term_positions.append(i)
                        break  # Found a match, move to next word
            
            if not term_positions:
                self.logger.warning("No search terms found in text")
                return ""
            
            # Create windows around each term position
            windows = set()
            for pos in term_positions:
                start = max(0, pos - self.window_size // 2)
                end = min(len(words), pos + self.window_size // 2)
                windows.add((start, end))
            
            # Merge overlapping windows
            merged_windows = self._merge_overlapping_windows(windows)
            
            # Extract text from merged windows
            for start, end in merged_windows:
                section_words = words[start:end]
                filtered_sections.append(" ".join(section_words))
            
            filtered_text = "\n\n".join(filtered_sections)
            
            # Log statistics
            original_words = len(words)
            filtered_words = len(filtered_text.split())
            reduction = ((original_words - filtered_words) / original_words) * 100
            
            self.logger.info(f"Text filtering: {original_words} → {filtered_words} words ({reduction:.1f}% reduction)")
            self.logger.info(f"Found {len(term_positions)} search term matches in {len(merged_windows)} sections")
            
            return filtered_text
            
        except Exception as e:
            self.logger.error(f"Error filtering text: {e}")
            return combined_text
    
    def _merge_overlapping_windows(self, windows: Set[tuple]) -> List[tuple]:
        """Merge overlapping or adjacent windows"""
        if not windows:
            return []
        
        # Sort windows by start position
        sorted_windows = sorted(windows)
        merged = []
        current_start, current_end = sorted_windows[0]
        
        for start, end in sorted_windows[1:]:
            # If windows overlap or are adjacent, merge them
            if start <= current_end + 100:  # Allow 100 word gap
                current_end = max(current_end, end)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = start, end
        
        merged.append((current_start, current_end))
        return merged
