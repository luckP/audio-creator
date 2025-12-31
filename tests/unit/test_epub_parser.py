"""Unit tests for EpubParser."""
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.parsers.epub_parser import EpubParser
from app.parsers.base_parser import ParsedDocument

class TestEpubParser(unittest.TestCase):
    """Test cases for EpubParser."""

    def setUp(self):
        self.parser = EpubParser()
        self.test_path = Path("test_book.epub")

    @patch("app.parsers.epub_parser.epub.read_epub")
    def test_parse_valid_epub(self, mock_read_epub):
        """Test parsing a valid EPUB file."""
        # Setup mock book
        mock_book = MagicMock()
        mock_read_epub.return_value = mock_book
        
        # Mock metadata
        mock_book.get_metadata.side_effect = lambda namespace, name: {
            ('DC', 'title'): [('My Ebook', {})],
            ('DC', 'creator'): [('Ebook Author', {})]
        }.get((namespace, name))

        # Mock items (chapters)
        # Item 1: Valid chapter
        item1 = MagicMock()
        item1.get_type.return_value = 1  # ITEM_DOCUMENT = 1 in ebooklib (usually 9, but let's mock the constant behavior or just type)
        # Actually better to mock the constant in the module but simpler to just matching what code does:
        # code checks: item.get_type() == ebooklib.ITEM_DOCUMENT
        # We need to ensure ITEM_DOCUMENT matches what we set.
        
        with patch("app.parsers.epub_parser.ebooklib.ITEM_DOCUMENT", 9):
            item1.get_type.return_value = 9
            item1.get_content.return_value = b"<html><body><h1>Chapter 1</h1><p>Content.</p></body></html>"

            # Item 2: Empty/Ignored
            item2 = MagicMock()
            item2.get_type.return_value = 9
            item2.get_content.return_value = b"<html><body></body></html>"

            mock_book.spine = [('id1', 'yes'), ('id2', 'yes')]
            mock_book.get_item_with_id.side_effect = lambda x: {'id1': item1, 'id2': item2}.get(x)

            with patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.is_file", return_value=True):
                
                result = self.parser.parse(self.test_path)

        self.assertEqual(result.title, "My Ebook")
        self.assertEqual(result.author, "Ebook Author")
        self.assertEqual(len(result.chapters), 1)
        self.assertEqual(result.chapters[0].title, "Chapter 1")
        # Content now preserves newlines between block elements
        self.assertEqual(result.chapters[0].content, "Chapter 1\nContent.")
        
    @patch("app.parsers.epub_parser.epub.read_epub")
    def test_parse_error(self, mock_read_epub):
        """Test handling of EPUB reading errors."""
        mock_read_epub.side_effect = Exception("Bad zip")

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_file", return_value=True):
            
            with self.assertRaises(RuntimeError):
                self.parser.parse(self.test_path)
