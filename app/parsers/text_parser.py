"""Text file parser implementation."""

from pathlib import Path
import chardet

from .base_parser import BaseParser, ParsedDocument


class TextParser(BaseParser):
    """Parser for plain text (.txt) files."""

    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse a text file and return a structured document.

        Args:
            file_path: Path to the .txt file.

        Returns:
            ParsedDocument containing the file content.
        
        Raises:
            FileNotFoundError: If file not found.
            ValueError: If file is not a valid text file.
        """
        self.validate_file(file_path)

        # Try UTF-8 first (standard and most common)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # If UTF-8 fails, try to detect the encoding
            encoding = self._detect_encoding(file_path)
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
            except (UnicodeDecodeError, LookupError):
                # Last resort: replace errors
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except Exception as exc:
                    raise ValueError(f"Could not decode file {file_path}: {exc}") from exc

        # Basic cleanup: normalize line endings
        content = content.replace("\r\n", "\n")

        return ParsedDocument(
            title=file_path.stem.replace("_", " ").title(),
            content=content,
            chapters=[]  # Text files usually don't have structured chapters
        )

    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding using chardet.
        Defaults to 'latin-1' if detection fails, as it covers most bytes.
        """
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read(10000)  # Read first 10KB
            
            result = chardet.detect(raw_data)
            encoding = result.get("encoding")
            
            # chardet can return None or very low confidence
            if encoding:
                return encoding
            return "latin-1"
        except OSError:
            return "latin-1"
