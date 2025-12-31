"""Text cleaning and normalization utilities."""

import re
from typing import List

class TextCleaner:
    """Processor to clean and normalize text extracted from documents."""

    def clean(self, text: str) -> str:
        """
        Main entry point to clean text. Applies a series of filters.
        
        Args:
            text: Raw input text.
            
        Returns:
            Cleaned and normalized text.
        """
        if not text:
            return ""

        # 1. Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 2. Fix hyphenation at line breaks (e.g. "impor-\ntant")
        # Matches: word ending in hyphen, newline, start of next word (lowercase)
        text = re.sub(r'(\w+)-\n([a-z])', r'\1\2', text)

        # 3. Remove common page artifacts (e.g. "Page 1", "- 1 -")
        # This is surprisingly hard to do safely without false positives.
        # We process line by line for this.
        lines = text.split('\n')
        cleaned_lines = self._remove_artifacts(lines)
        
        # 4. Normalize whitespace
        # Join lines back. Double newlines for paragraphs, single for wrapping.
        # However, many PDFs have hard wraps.
        text = self._reflow_text(cleaned_lines)

        return text.strip()

    def _remove_artifacts(self, lines: List[str]) -> List[str]:
        """Remove headers, footers, and page numbers."""
        cleaned = []
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                cleaned.append("")
                continue

            # Detect Page Numbers
            # Matches: "1", "Page 1", "- 1 -", "1 of 20"
            if re.match(r'^-?\s*(?:Page\s+)?\d+(?:\s+of\s+\d+)?\s*-?$', stripped, re.IGNORECASE):
                continue
                
            cleaned.append(line)
        return cleaned

    def _reflow_text(self, lines: List[str]) -> str:
        """
        Intelligent text reflow.
        Joins lines that seem to be part of the same paragraph.
        Keeps double newlines as paragraph breaks.
        """
        result = []
        current_paragraph = []

        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                # Empty line -> Paragraph break
                if current_paragraph:
                    result.append(" ".join(current_paragraph))
                    current_paragraph = []
                continue
            
            # Heuristic: If line ends with sentence punctuation, it might be the end of a thought
            # but usually in PDFs, paragraphs are visuals.
            # We'll assume any consecutive non-empty lines are part of the same paragraph
            # unless we detect a list item or header (TODO).
            current_paragraph.append(stripped)

        # Flush last paragraph
        if current_paragraph:
            result.append(" ".join(current_paragraph))

        return "\n\n".join(result)
