"""Metadata extraction from text content."""

import re
from typing import Dict, Any, Optional

class MetadataExtractor:
    """Enriches document metadata by analyzing content."""

    def extract(self, text: str, existing_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract metadata from text and merge with existing.
        
        Args:
            text: First few pages/paragraphs of text usually suffice.
            existing_metadata: Dict matching ParsedDocument metadata.
            
        Returns:
            Updated metadata dictionary.
        """
        metadata = existing_metadata.copy() if existing_metadata else {}
        
        # 1. Extract Emails
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if emails and 'email' not in metadata:
             metadata['contact_email'] = emails[0] # Just take first one found

        # 2. Extract Year (copyright)
        # Look for "Copyright (c) 2023" or similar
        copyright_match = re.search(r'copyright\s+(?:\(c\)\s+)?(\d{4})', text, re.IGNORECASE)
        if copyright_match and 'publication_year' not in metadata:
             metadata['publication_year'] = int(copyright_match.group(1))

        # 3. Extract ISBN
        # 10 or 13 digits, allowing hyphens
        # ISBN-13: 978-3-16-148410-0
        # Regex captures the first digit/hyphen group until whitespace
        isbn_match = re.search(r'ISBN(?:-13|10)?\s*:?\s*([\d\-]{10,17}X?)', text, re.IGNORECASE)
        if isbn_match and 'isbn' not in metadata:
             # Basic cleanup
             isbn = isbn_match.group(1).strip()
             if len(re.sub(r'[^\dX]', '', isbn)) >= 10:
                metadata['isbn'] = isbn

        return metadata
