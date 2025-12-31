"""Tests for base parser interface and factory."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.parsers.base_parser import BaseParser, ParsedDocument, ParsedChapter
from app.parsers import get_parser, register_parser, _PARSER_REGISTRY

# --- Fixtures & Morks ---

class MockParser(BaseParser):
    """Concrete implementation for testing."""
    def parse(self, file_path: Path) -> ParsedDocument:
        return ParsedDocument(title="Mock", content="Content")

@pytest.fixture
def clear_registry():
    """Clear registry before and after tests."""
    original_registry = _PARSER_REGISTRY.copy()
    _PARSER_REGISTRY.clear()
    yield
    _PARSER_REGISTRY.clear()
    _PARSER_REGISTRY.update(original_registry)

# --- Base Parser Tests ---

def test_base_parser_validate_file_exists(tmp_path):
    """Test validation of existing file."""
    f = tmp_path / "test.txt"
    f.touch()
    
    parser = MockParser()
    # Should not raise exception
    parser.validate_file(f)

def test_base_parser_validate_file_not_found():
    """Test validation of missing file."""
    parser = MockParser()
    with pytest.raises(FileNotFoundError):
        parser.validate_file(Path("nonexistent.txt"))

def test_base_parser_validate_not_a_file(tmp_path):
    """Test validation of directory instead of file."""
    d = tmp_path / "testdir"
    d.mkdir()
    
    parser = MockParser()
    with pytest.raises(ValueError):
        parser.validate_file(d)

def test_parsed_document_structure():
    """Test data class integrity."""
    doc = ParsedDocument(
        title="Test",
        content="Full content",
        chapters=[
            ParsedChapter(title="Ch1", content="Text1", number=1)
        ],
        metadata={"key": "value"}
    )
    
    assert doc.title == "Test"
    assert len(doc.chapters) == 1
    assert doc.chapters[0].title == "Ch1"
    assert doc.metadata["key"] == "value"

# --- Factory/Registry Tests ---

def test_register_and_get_parser(clear_registry, tmp_path):
    """Test registering and retrieving a parser."""
    register_parser(".mock", MockParser)
    
    f = tmp_path / "test.mock"
    parser = get_parser(f)
    
    assert isinstance(parser, MockParser)

def test_get_parser_unsupported_extension(clear_registry, tmp_path):
    """Test error for unsupported extension."""
    f = tmp_path / "test.unknown"
    
    with pytest.raises(ValueError) as exc:
        get_parser(f)
    
    assert "No parser supported" in str(exc.value)

def test_register_parser_normalizes_extension(clear_registry):
    """Test that extensions are normalized (lowercase, added dot)."""
    register_parser("MOCK", MockParser)
    
    # Should work with lowercase and dot
    assert ".mock" in _PARSER_REGISTRY
    assert _PARSER_REGISTRY[".mock"] == MockParser

def test_get_parser_normalizes_input_extension(clear_registry, tmp_path):
    """Test that input file extension is case insensitive."""
    register_parser(".mock", MockParser)
    
    f = tmp_path / "TEST.MOCK"
    parser = get_parser(f)
    
    assert isinstance(parser, MockParser)
