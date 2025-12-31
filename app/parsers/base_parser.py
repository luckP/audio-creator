"""Base parser interface and data structures."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any


from enum import Enum

class Language(str, Enum):
    """Supported languages for audio generation."""
    EN = "en"
    PT = "pt"
    ES = "es"


@dataclass
class ParsedChapter:
    """Represents a chapter extracted from a document."""
    title: str
    content: str
    number: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDocument:
    """
    Represents the result of parsing a document file.
    Result includes the document metadata and list of chapters.
    """
    title: str
    content: str  # Full content text if not chapterized, or strict full text
    chapters: List[ParsedChapter] = field(default_factory=list)
    author: Optional[str] = None
    language: Language = Language.EN
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseParser(ABC):
    """Abstract base class for all document parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse a file and return a structured document.

        Args:
            file_path: Path to the source file.

        Returns:
            ParsedDocument object containing title, content, and chapters.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is invalid or unsupported.
            RuntimeError: If parsing fails.
        """

    def validate_file(self, file_path: Path) -> None:
        """
        Basic validation for file existence.
        
        Args:
            file_path: Path to check.
            
        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
