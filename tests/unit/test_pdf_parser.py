"""Unit tests for PDFParser."""
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.parsers.pdf_parser import PDFParser
from app.parsers.base_parser import ParsedDocument

class TestPDFParser(unittest.TestCase):
    """Test cases for PDFParser."""

    def setUp(self):
        self.parser = PDFParser()
        self.test_path = Path("test_document.pdf")

    @patch("app.parsers.pdf_parser.pdfplumber.open")
    def test_parse_valid_pdf(self, mock_open):
        """Test parsing a valid PDF file."""
        # Setup mock PDF
        mock_pdf = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        # Setup metadata
        mock_pdf.metadata = {"Title": "Test PDF", "Author": "Test Author"}
        
        # Setup pages
        page1 = MagicMock()
        page1.extract_text.return_value = "Page 1 content."
        page2 = MagicMock()
        page2.extract_text.return_value = "Page 2 content."
        mock_pdf.pages = [page1, page2]

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_file", return_value=True):
            
            result = self.parser.parse(self.test_path)

        self.assertIsInstance(result, ParsedDocument)
        self.assertEqual(result.title, "Test PDF")
        self.assertEqual(result.author, "Test Author")
        self.assertIn("Page 1 content.", result.content)
        self.assertIn("Page 2 content.", result.content)

    @patch("app.parsers.pdf_parser.pdfplumber.open")
    def test_parse_no_metadata(self, mock_open):
        """Test parsing where metadata is missing."""
        mock_pdf = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_pdf
        mock_pdf.metadata = {}  # Empty metadata
        
        page1 = MagicMock()
        page1.extract_text.return_value = "Just some text."
        mock_pdf.pages = [page1]

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_file", return_value=True):
            
            # Should derive title from filename
            result = self.parser.parse(Path("my_report.pdf"))

        self.assertEqual(result.title, "My Report")
        self.assertIsNone(result.author)
        self.assertEqual(result.content, "Just some text.")

    @patch("app.parsers.pdf_parser.pdfplumber.open")
    def test_parse_error(self, mock_open):
        """Test handling of parsing errors."""
        mock_open.side_effect = Exception("Corrupt file")

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_file", return_value=True):
            
            with self.assertRaises(RuntimeError) as cm:
                self.parser.parse(self.test_path)
            
            self.assertIn("Failed to parse PDF file", str(cm.exception))

    def test_file_not_found(self):
        """Test validation for missing file."""
        with patch("pathlib.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                self.parser.parse(Path("ghost.pdf"))
