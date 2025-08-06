"""Filter text to relevant sections based on search terms."""

import re
from typing import List, Set
from utils.logger import logger

class TextFilter:
    """Filter text to only include sections near search terms."""
    
    def __init__(self, search_terms: List[str], window_size: int = 1000):
        self.search_terms = [term.lower() for term in search_terms]
        self.window_size = window_size
        self.logger = logger
    
    def filter_text(self, combined_text: str) -> str:
        """Filter text to only include sections within window_size words of search terms."""
        if not combined_text or not self.search_terms:
            return combined_text
        
        words = combined_text.split()
        term_positions = self._find_search_term_positions(words)
        
        if not term_positions:
            self.logger.warning("No search terms found in text")
            return ""
        
        windows = self._create_windows(term_positions, len(words))
        merged_windows = self._merge_overlapping_windows(windows)
        filtered_sections = self._extract_sections(words, merged_windows)
        
        filtered_text = "\n\n".join(filtered_sections)
        self._log_filtering_stats(words, filtered_text, term_positions, merged_windows)
        
        return filtered_text
    
    def _find_search_term_positions(self, words: List[str]) -> List[int]:
        """Find positions of search terms in word list."""
        positions = []
        for i, word in enumerate(words):
            word_lower = word.lower()
            if any(term in word_lower for term in self.search_terms):
                positions.append(i)
        return positions
    
    def _create_windows(self, positions: List[int], total_words: int) -> Set[tuple]:
        """Create windows around search term positions."""
        windows = set()
        half_window = self.window_size // 2
        
        for pos in positions:
            start = max(0, pos - half_window)
            end = min(total_words, pos + half_window)
            windows.add((start, end))
        
        return windows
    
    def _extract_sections(self, words: List[str], windows: List[tuple]) -> List[str]:
        """Extract text sections from windows."""
        sections = []
        for start, end in windows:
            section_words = words[start:end]
            sections.append(" ".join(section_words))
        return sections
    
    def _log_filtering_stats(self, original_words: List[str], filtered_text: str, 
                           term_positions: List[int], merged_windows: List[tuple]):
        """Log filtering statistics."""
        original_count = len(original_words)
        filtered_count = len(filtered_text.split())
        reduction = ((original_count - filtered_count) / original_count) * 100
        
        self.logger.info(f"Text filtering: {original_count} → {filtered_count} words ({reduction:.1f}% reduction)")
        self.logger.info(f"Found {len(term_positions)} search term matches in {len(merged_windows)} sections")
    
    def _merge_overlapping_windows(self, windows: Set[tuple]) -> List[tuple]:
        """Merge overlapping or adjacent windows."""
        if not windows:
            return []
        
        sorted_windows = sorted(windows)
        merged = []
        current_start, current_end = sorted_windows[0]
        
        for start, end in sorted_windows[1:]:
            if start <= current_end + 100:  # Allow 100 word gap
                current_end = max(current_end, end)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = start, end
        
        merged.append((current_start, current_end))
        return merged
