"""
Parser package initialization.
Exports the base parser interface and factory method for getting parsers.
"""

from pathlib import Path
from typing import Dict, Type, Optional

from .base_parser import BaseParser, ParsedDocument, ParsedChapter
from .text_parser import TextParser

# Registry of supported parsers
_PARSER_REGISTRY: Dict[str, Type[BaseParser]] = {}


def register_parser(extension: str, parser_class: Type[BaseParser]) -> None:
    """
    Register a parser class for a specific file extension.
    
    Args:
        extension: File extension (e.g., '.txt', '.pdf').
        parser_class: Class implementing BaseParser.
    """
    ext = extension.lower()
    if not ext.startswith('.'):
        ext = '.' + ext
    _PARSER_REGISTRY[ext] = parser_class

# Auto-register default parsers
register_parser('.txt', TextParser)
register_parser('.md', TextParser)


def get_parser(file_path: str | Path) -> BaseParser:
    """
    Get an instance of the appropriate parser for the given file.
    
    Args:
        file_path: Path to the file to be parsed.
        
    Returns:
        An instance of the appropriate parser.
        
    Raises:
        ValueError: If no parser is found for the file extension.
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    parser_class = _PARSER_REGISTRY.get(ext)
    
    if not parser_class:
        supported = ", ".join(_PARSER_REGISTRY.keys())
        raise ValueError(f"No parser supported for extension '{ext}'. Supported: {supported}")
        
    return parser_class()
