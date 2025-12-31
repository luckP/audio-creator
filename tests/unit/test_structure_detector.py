"""Unit tests for StructureDetector."""
import unittest
from app.processors.structure_detector import StructureDetector
from app.parsers.base_parser import ParsedChapter

class TestStructureDetector(unittest.TestCase):
    """Test cases for StructureDetector."""

    def setUp(self):
        self.detector = StructureDetector()

    def test_detect_explicit_chapters(self):
        """Test finding 'Chapter 1' style references."""
        text = """
Introduction text here.

Chapter 1
The story begins.

Chapter 2
It continues.
"""
        chapters = self.detector.split_into_chapters(text)
        self.assertEqual(len(chapters), 3) # Intro, Ch1, Ch2
        self.assertEqual(chapters[1].title, "Chapter 1")
        self.assertIn("The story begins", chapters[1].content)

    def test_detect_all_caps_headers(self):
        """Test finding all-caps headers."""
        text = """
PREFACE
Some preface text.

THE BEGINNING
It was a dark night.
"""
        chapters = self.detector.split_into_chapters(text)
        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0].title, "PREFACE")
        self.assertEqual(chapters[1].title, "THE BEGINNING")

    def test_no_structure(self):
        """Test flat text returns empty list (indicating no split)."""
        text = "Just a short story with no specific chapters."
        chapters = self.detector.split_into_chapters(text)
        self.assertEqual(chapters, [])

    def test_numbered_sections(self):
        """Test '1. Title' format."""
        text = """
1. First
Content.
2. Second
Content.
"""
        chapters = self.detector.split_into_chapters(text)
        # Note: the empty start means text before "1. First" is effectively empty, so skipped?
        # Let's trace logic:
        # loop start. line empty.
        # "1. First" -> Header. current_lines=[] (empty). Don't save previous.
        # Start "1. First".
        # ...
        # So we expect 2 chapters.
        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0].title, "1. First")
