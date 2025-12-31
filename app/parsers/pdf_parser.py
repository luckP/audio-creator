"""PDF document parser using pdfplumber."""

from pathlib import Path

import pdfplumber

from .base_parser import BaseParser, ParsedDocument


class PDFParser(BaseParser):
    """Parser for PDF documents."""

    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse a PDF file and extract text content.

        Args:
            file_path: Path to the PDF file.

        Returns:
            ParsedDocument containing the extracted text.
        """
        self.validate_file(file_path)

        text_content = []
        metadata = {}
        title = file_path.stem.replace('_', ' ').title()
        author = None

        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata if available
                if pdf.metadata:
                    metadata = pdf.metadata
                    if 'Title' in metadata and metadata['Title']:
                        title = metadata['Title']
                    if 'Author' in metadata and metadata['Author']:
                        author = metadata['Author']

                # Extract text from each page
                for page in pdf.pages:
                    # Basic extraction
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF file: {e}") from e

        full_text = "\n\n".join(text_content)

        if not full_text.strip():
            # Warning: Empty PDF or image-only
            # In a real app we might want a specific error or OCR fallback
            pass

        return ParsedDocument(
            title=title,
            author=author,
            content=full_text,
            chapters=[],  # Basic PDF parsing doesn't auto-detect chapters yet
            metadata=metadata
        )
