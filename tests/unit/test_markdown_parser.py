"""Unit tests for MarkdownParser."""
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

from app.parsers.markdown_parser import MarkdownParser
from app.parsers.base_parser import ParsedDocument
from app.parsers.base_parser import ParsedChapter

class TestMarkdownParser(unittest.TestCase):
    """Test cases for MarkdownParser."""

    def setUp(self):
        self.parser = MarkdownParser()
        self.test_path = Path("test_book.md")

    def test_parse_simple_markdown(self):
        """Test parsing simple markdown with no metadata."""
        content = """# My Book
This is a short intro.

## Chapter 1
Once upon a time.

## Chapter 2
The end.
"""
        with patch("builtins.open", mock_open(read_data=content)), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_file", return_value=True):
            
            result = self.parser.parse(self.test_path)

        self.assertEqual(result.title, "My Book")
        # Expect 3: Introduction (preamble) + Chapter 1 + Chapter 2
        self.assertEqual(len(result.chapters), 3)
        self.assertEqual(result.chapters[0].title, "Introduction")
        self.assertEqual(result.chapters[1].title, "Chapter 1")
        self.assertEqual(result.chapters[1].content, "Once upon a time.")
        self.assertEqual(result.chapters[2].title, "Chapter 2")

    def test_parse_with_front_matter(self):
        """Test parsing markdown with YAML front matter."""
        content = """---
title: The Great Adventure
author: Jane Doe
---
# Introduction
Here it begins.

# Chapter One
The journey starts.
"""
        # Note: Logic splits by highest freq header. Here we have # Intro and # Chapter One.
        # Both start with '# ', so split_prefix will be '# '.
        
        with patch("builtins.open", mock_open(read_data=content)), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_file", return_value=True):
            
            result = self.parser.parse(self.test_path)

        self.assertEqual(result.title, "The Great Adventure")
        self.assertEqual(result.author, "Jane Doe")
        self.assertEqual(len(result.chapters), 2)
        self.assertEqual(result.chapters[0].title, "Introduction")
        self.assertEqual(result.chapters[1].title, "Chapter One")

    def test_parse_nested_headers(self):
        """Test parsing where only H2 are chapters (common pattern)."""
        content = """# Main Title
Intro text.

## Chapter 1
Content 1.

### Section 1.1
Subcontent.

## Chapter 2
Content 2.
"""
        with patch("builtins.open", mock_open(read_data=content)), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_file", return_value=True):
            
            result = self.parser.parse(self.test_path)

        # parser logic: 1 H1, multiple H2s -> split by '## '
        self.assertEqual(result.title, "Main Title")
        # Expect 3: Introduction + Chapter 1 + Chapter 2
        self.assertEqual(len(result.chapters), 3)
        self.assertEqual(result.chapters[0].title, "Introduction")
        self.assertEqual(result.chapters[1].title, "Chapter 1")
        
        # Check that subheaders are preserved in content
        self.assertIn("### Section 1.1", result.chapters[1].content)

    def test_no_headers(self):
        """Test parsing markdown with no headers (single block)."""
        content = "Just some text without headers."
        
        with patch("builtins.open", mock_open(read_data=content)), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_file", return_value=True):
            
            result = self.parser.parse(self.test_path)

        self.assertEqual(len(result.chapters), 0)
        self.assertEqual(result.content, content)
