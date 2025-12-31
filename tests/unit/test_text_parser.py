"""Tests for the TextParser."""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from app.parsers.text_parser import TextParser
from app.parsers.base_parser import ParsedDocument

# Sample content with different encodings
UTF8_CONTENT = "Hello, world! © 2024"
LATIN1_CONTENT = "Olá Mundo, café e pão".encode("latin-1")


def test_text_parser_basic(tmp_path):
    """Test parsing a simple valid UTF-8 text file."""
    f = tmp_path / "simple.txt"
    f.write_text(UTF8_CONTENT, encoding="utf-8")
    
    parser = TextParser()
    doc = parser.parse(f)
    
    assert isinstance(doc, ParsedDocument)
    assert doc.title == "Simple"
    assert doc.content == UTF8_CONTENT
    assert len(doc.chapters) == 0


def test_text_parser_encoding_detection(tmp_path):
    """Test parsing a file with non-utf-8 encoding."""
    f = tmp_path / "latin1.txt"
    with open(f, "wb") as f_out:
        f_out.write(LATIN1_CONTENT)
        
    parser = TextParser()
    doc = parser.parse(f)
    
    assert "café" in doc.content
    assert "pão" in doc.content


def test_text_parser_invalid_file(tmp_path):
    """Test that validating a non-existent file raises error."""
    parser = TextParser()
    with pytest.raises(FileNotFoundError):
        parser.parse(tmp_path / "non_existent.txt")


def test_text_parser_title_formatting(tmp_path):
    """Test title extraction from filename."""
    f = tmp_path / "my_awesome_book.txt"
    f.write_text("content", encoding="utf-8")
    
    parser = TextParser()
    doc = parser.parse(f)
    
    assert doc.title == "My Awesome Book"


def test_text_parser_normalize_lines(tmp_path):
    """Test that Windows line endings are normalized."""
    content = "Line 1\r\nLine 2\r\nLine 3"
    f = tmp_path / "windows.txt"
    f.write_text(content, encoding="utf-8")
    
    parser = TextParser()
    doc = parser.parse(f)
    
    assert "Line 1\nLine 2\nLine 3" == doc.content
