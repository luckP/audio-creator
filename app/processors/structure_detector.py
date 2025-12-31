"""Structure detection for flat text documents."""

import re
from typing import List, Optional, Tuple
from app.models.chapter import Chapter  # Or use ParsedChapter from base_parser ideally to keep layers clean
# Let's use ParsedChapter to avoid DB dependency in processor
from app.parsers.base_parser import ParsedChapter

class StructureDetector:
    """Detects chapters and sections in flat text."""

    def __init__(self):
         # Regex for common chapter headings
         # 1. "Chapter 1", "CHAPTER I", "Chapter One"
         # 2. "1. Introduction"
         # 3. All caps lines like "THE END" (heuristically)
         self.chapter_patterns = [
             r'^chapter\s+[\dIVX]+',
             r'^chapter\s+\w+$',
             r'^\d+\.\s+\w+',
             r'^[IVX]+\.\s+\w+',
         ]

    def split_into_chapters(self, text: str) -> List[ParsedChapter]:
        """
        Scan text for chapter boundaries and split it.
        
        Args:
            text: clean, full-text content.
            
        Returns:
            List of ParsedChapter objects. 
            If no structure found, returns [] (or maybe 1 chapter? usually [] lets caller decide).
        """
        lines = text.split('\n')
        chapters: List[ParsedChapter] = []
        
        current_title = "Introduction"
        current_lines = []
        chapter_num = 1
        
        found_any_structure = False

        for line in lines:
            line_stripped = line.strip()
            
            if self._is_chapter_header(line_stripped):
                found_any_structure = True
                
                # Close previous chapter
                if current_lines:
                    # Don't save empty intro if it's just whitespace
                    content = "\n".join(current_lines).strip()
                    if content:
                        chapters.append(ParsedChapter(
                            title=current_title,
                            content=content,
                            number=chapter_num
                        ))
                        chapter_num += 1
                
                # Start new
                current_title = line_stripped
                current_lines = []
            else:
                current_lines.append(line)
        
        # Flush last
        if current_lines:
            content = "\n".join(current_lines).strip()
            if content:
                # If we never found ANY structure, return empty list meant "no chapters detected"
                # rather than wrapping the whole thing in "Introduction".
                if not found_any_structure:
                    return []
                    
                chapters.append(ParsedChapter(
                    title=current_title,
                    content=content,
                    number=chapter_num
                ))

        return chapters

    def _is_chapter_header(self, line: str) -> bool:
        """Check if a line looks like a chapter header."""
        if not line:
            return False
            
        # Check explicit patterns
        for pattern in self.chapter_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
                
        # Check All Caps (heuristically, length > 3, less than 50 chars)
        # e.g. "THE BEGINNING"
        if line.isupper() and 3 < len(line) < 50:
             # Make sure it has some letters
             if re.search(r'[A-Z]', line):
                 return True
                 
        return False
