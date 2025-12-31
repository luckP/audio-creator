"""Unit tests for MetadataExtractor."""
import unittest
from app.processors.metadata_extractor import MetadataExtractor

class TestMetadataExtractor(unittest.TestCase):
    """Test cases for MetadataExtractor."""

    def setUp(self):
        self.extractor = MetadataExtractor()

    def test_extract_isbn_year(self):
        """Test finding ISBN and year."""
        text = """
My Awesome Book
Copyright (c) 2024 by Author Name
ISBN: 978-3-16-148410-0
All rights reserved.
"""
        meta = self.extractor.extract(text)
        self.assertEqual(meta.get('publication_year'), 2024)
        self.assertIn("978-3-16", meta.get('isbn'))

    def test_extract_email(self):
        """Test finding email addresses."""
        text = "Contact us at support@example.com for info."
        meta = self.extractor.extract(text)
        self.assertEqual(meta.get('contact_email'), "support@example.com")

    def test_merge_existing(self):
        """Test preserving existing metadata."""
        existing = {'author': 'Existing Author'}
        text = "Copyright 1999"
        meta = self.extractor.extract(text, existing)
        
        self.assertEqual(meta.get('author'), 'Existing Author')
        self.assertEqual(meta.get('publication_year'), 1999)
