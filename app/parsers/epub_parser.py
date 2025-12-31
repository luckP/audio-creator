"""EPUB document parser using EbookLib."""

import warnings
from pathlib import Path
from typing import List, Optional

# EbookLib triggers UserWarnings about XML parsing that we can ignore for now
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import ebooklib
    from ebooklib import epub

from bs4 import BeautifulSoup

from .base_parser import BaseParser, ParsedDocument, ParsedChapter

class EpubParser(BaseParser):
    """Parser for EPUB documents."""

    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse an EPUB file, extracting content chapter by chapter.

        Args:
            file_path: Path to the EPUB file.

        Returns:
            ParsedDocument containing structured chapters.
        """
        self.validate_file(file_path)

        try:
            # Read EPUB book
            # set ignore_ncx=True might speed it up if we iterate spine manually, 
            # but usually defaults are fine.
            book = epub.read_epub(str(file_path))
        except Exception as e:
            raise RuntimeError(f"Failed to read EPUB file: {e}") from e

        # Extract Metadata
        title = self._get_metadata(book, 'DC', 'title') or file_path.stem.replace('_', ' ').title()
        author = self._get_metadata(book, 'DC', 'creator')
        
        # Extract Chapters
        chapters: List[ParsedChapter] = []
        full_text_parts = []
        chapter_num = 1

        # Iterate through the spine to get reading order
        for item_id, _linear in book.spine:
            item = book.get_item_with_id(item_id)
            if not item:
                continue
                
            # We are interested in valid text chapters
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content()
                text_content = self._html_to_text(content)
                
                # Skip if empty or just whitespace
                if not text_content.strip():
                    continue

                # Try to find a title for this chapter 
                # (EbookLib doesn't easily give chapter titles from spine without parsing NCX)
                # For now, we'll use "Chapter N" or try to find first header
                chapter_title = f"Chapter {chapter_num}"
                
                # Simple heuristic: first line is title if short
                lines = text_content.split('\n')
                if lines and len(lines[0]) < 100:
                    chapter_title = lines[0].strip()

                chapters.append(ParsedChapter(
                    title=chapter_title,
                    content=text_content,
                    number=chapter_num
                ))
                full_text_parts.append(text_content)
                chapter_num += 1

        return ParsedDocument(
            title=title,
            author=author,
            content="\n\n".join(full_text_parts),
            chapters=chapters,
            metadata={}
        )

    def _get_metadata(self, book, namespace: str, name: str) -> Optional[str]:
        """Helper to safely extract metadata from the book."""
        try:
            meta = book.get_metadata(namespace, name)
            if meta:
                return meta[0][0]
        except (IndexError, KeyError):
            pass
        return None

    def _html_to_text(self, html_content: bytes) -> str:
        """Convert HTML content to clean text."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text(separator='\n')
        
        # Collapse whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
