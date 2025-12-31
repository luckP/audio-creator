"""Unit tests for TextCleaner."""
import unittest
from app.processors.text_cleaner import TextCleaner

class TestTextCleaner(unittest.TestCase):
    """Test cases for TextCleaner."""

    def setUp(self):
        self.cleaner = TextCleaner()

    def test_fix_hyphenation(self):
        """Test fixing hyphenated words across lines."""
        raw = "This is an impor-\ntant test."
        expected = "This is an important test."
        # Note: clean() also reflows text, so newlines become spaces usually.
        # But our regex logic handles the join: "impor-" + "\n" + "tant" -> "important"
        # Then reflow joins lines: "This is an important" + " " + "test."
        
        result = self.cleaner.clean(raw)
        self.assertEqual(result, expected)

    def test_remove_page_numbers(self):
        """Test removing common page offsets."""
        raw = """
Start of page.
Page 1
End of page.
- 2 -
Next page.
"""
        result = self.cleaner.clean(raw)
        self.assertNotIn("Page 1", result)
        self.assertNotIn("- 2 -", result)
        self.assertIn("Start of page.", result)

    def test_remove_line_breaks(self):
        """Test reflowing hard-wrapped text into paragraphs."""
        raw = """This is a sentence
that was split
across multiple lines."""
        
        expected = "This is a sentence that was split across multiple lines."
        result = self.cleaner.clean(raw)
        self.assertEqual(result, expected)

    def test_preserve_paragraphs(self):
        """Test keeping paragraph structure (double newlines)."""
        raw = """Paragraph one.

Paragraph two is here.
"""
        expected = "Paragraph one.\n\nParagraph two is here."
        result = self.cleaner.clean(raw)
        self.assertEqual(result, expected)

    def test_empty_string(self):
        """Test handling empty input."""
        self.assertEqual(self.cleaner.clean(""), "")
        self.assertEqual(self.cleaner.clean(None), "")
