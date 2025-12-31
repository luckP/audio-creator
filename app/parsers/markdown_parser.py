"""Markdown document parser."""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

from .base_parser import BaseParser, ParsedDocument, ParsedChapter

class MarkdownParser(BaseParser):
    """Parser for Markdown documents with structure detection."""

    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Parse a Markdown file, extracting metadata and chapters.

        Args:
            file_path: Path to the Markdown file.

        Returns:
            ParsedDocument containing title, metadata, and chapters.
        """
        self.validate_file(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Extract Front Matter (YAML-like metadata)
        metadata, content = self._extract_front_matter(content)
        
        # 2. Determine Title
        title = metadata.get("title")
        author = metadata.get("author")
        
        # If no title in metadata, try to find the first H1
        if not title:
            h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
            else:
                title = file_path.stem.replace('_', ' ').replace('-', ' ').title()

        # 3. Detect Chapters
        chapters = self._parse_chapters(content)
        
        # If chapters were found, we might want to strip the first H1 from the text 
        # if it was used as the document title to avoid reading it twice, 
        # but for now we'll keep the full content in the main content field 
        # or just the intro text? 
        # The BaseParser.ParsedDocument design has 'content' (full text) AND 'chapters'.
        
        return ParsedDocument(
            title=title,
            author=author,
            content=content,
            chapters=chapters,
            metadata=metadata
        )

    def _extract_front_matter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Extract YAML-style front matter from the beginning of the content.
        Returns (metadata_dict, remaining_content).
        """
        metadata = {}
        # Regex for front matter: start of string, ---, content, ---
        match = re.match(r'^\s*---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        
        if match:
            yaml_text = match.group(1)
            remaining_content = content[match.end():]
            
            # Simple YAML parsing (key: value) to avoid a heavy dependency like PyYAML 
            # unless strictly necessary. keeping it simple for now.
            for line in yaml_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip().strip('"').strip("'")
            
            return metadata, remaining_content
        
        return metadata, content

    def _parse_chapters(self, content: str) -> List[ParsedChapter]:
        """
        Split content into chapters based on headers.
        Strategy:
        1. Scan for headers (#, ##, ###)
        2. Determine the "Chapter Level" (e.g. if we have H1s throughout, use H1. If only one H1, use H2).
        """
        lines = content.split('\n')
        chapters: List[ParsedChapter] = []
        
        # Heuristic: Count header frequencies to guess the structure
        h1_count = sum(1 for line in lines if line.startswith('# '))
        h2_count = sum(1 for line in lines if line.startswith('## '))
        
        # Default split level
        split_prefix = '## ' 
        
        if h1_count > 1:
            # Multiple H1s -> assume these are chapters
            split_prefix = '# '
        elif h2_count > 0:
            # One or zero H1s, but we have H2s -> assume H2s are chapters
            split_prefix = '## '
        else:
            # No clear chapter structure
            return []

        current_chapter_title = "Introduction"
        current_chapter_lines = []
        chapter_num = 1
        
        # Loop through lines to build chapters
        for line in lines:
            if line.startswith(split_prefix):
                # New Chapter Found
                # Save previous chapter if it has content
                if current_chapter_lines:
                    chapter_text = '\n'.join(current_chapter_lines).strip()
                    if chapter_text:
                        chapters.append(ParsedChapter(
                            title=current_chapter_title,
                            content=chapter_text,
                            number=chapter_num
                        ))
                        chapter_num += 1
                
                # Start new chapter
                current_chapter_title = line[len(split_prefix):].strip()
                current_chapter_lines = []
            else:
                current_chapter_lines.append(line)
        
        # Append the last chapter
        if current_chapter_lines:
            chapter_text = '\n'.join(current_chapter_lines).strip()
            if chapter_text:
                chapters.append(ParsedChapter(
                    title=current_chapter_title,
                    content=chapter_text,
                    number=chapter_num
                ))
                
        return chapters
