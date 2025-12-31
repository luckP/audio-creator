"""
Orchestration pipeline for converting documents to audiobooks.
"""
import logging
import shutil
import math
from pathlib import Path
from typing import List, Optional
import tempfile

from app.parsers.base_parser import ParsedDocument, ParsedChapter
from app.audio.generator import AudioGenerator
from app.audio.combiner import AudioCombiner
from app.audio.converter import AudioConverter

logger = logging.getLogger(__name__)

class AudioPipeline:
    """
    Orchestrates the conversion of a ParsedDocument into audio files.
    Manages temporary files, chunking, and stage transitions.
    """

    def __init__(self, output_dir: Path, voice: str = "Alex", speed: float = 1.0, format: str = "mp3"):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.format = format.lower()
        
        # Initialize components
        self.generator = AudioGenerator(voice=voice, rate=speed)
        self.combiner = AudioCombiner()
        self.converter = AudioConverter()

    def process_document(self, document: ParsedDocument) -> List[Path]:
        """
        Convert the entire document into audio files.
        
        If chapters exist, one file per chapter.
        If no chapters, one single file.
        
        Returns:
            List of paths to valid final audio files.
        """
        logger.info(f"Starting audio pipeline for '{document.title}'")
        final_files = []

        # Create a working directory for intermediate files
        with tempfile.TemporaryDirectory(prefix="audiobook_gen_") as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            logger.debug(f"Created temporary working directory: {temp_dir}")

            if document.chapters:
                total_chapters = len(document.chapters)
                for i, chapter in enumerate(document.chapters, 1):
                    logger.info(f"Processing Chapter {i}/{total_chapters}: {chapter.title}")
                    
                    try:
                        chapter_file = self._process_chapter(chapter, i, temp_dir)
                        if chapter_file:
                            final_files.append(chapter_file)
                    except Exception as e:
                        logger.error(f"Failed to process chapter {i}: {e}", exc_info=True)
                        # Continue to next chapter? Or fail hard?
                        # For now, log and continue, but user might end up with partial book.
            else:
                # Single block content
                logger.info("Processing single block content...")
                # Wrap content in a dummy chapter for uniform handling
                dummy_chapter = ParsedChapter(title=document.title, content=document.content, number=1)
                try:
                    chapter_file = self._process_chapter(dummy_chapter, 1, temp_dir)
                    if chapter_file:
                        final_files.append(chapter_file)
                except Exception as e:
                     logger.error(f"Failed to process document content: {e}", exc_info=True)

        logger.info(f"Pipeline complete. Generated {len(final_files)} files in {self.output_dir}")
        return final_files

    def _process_chapter(self, chapter: ParsedChapter, index: int, temp_dir: Path) -> Optional[Path]:
        """
        Process a single chapter: Chunk -> Generate -> Combine -> Convert.
        """
        if not chapter.content.strip():
            logger.warning(f"Chapter {index} is empty, skipping.")
            return None

        # 1. Chunking
        # 'say' command can hang on massive text blocks.
        # We split by newlines first, then maybe length strictly if lines are huge.
        chunks = self._chunk_text(chapter.content)
        
        if not chunks:
            return None

        chapter_temp_dir = temp_dir / f"ch_{index}"
        chapter_temp_dir.mkdir(exist_ok=True)
        
        chunk_files = []
        
        # 2. Generation (Text -> AIFF)
        for c_idx, text_chunk in enumerate(chunks):
            chunk_path = chapter_temp_dir / f"chunk_{c_idx:04d}.aiff"
            try:
                self.generator.generate_chunk(text_chunk, chunk_path)
                if chunk_path.exists():
                     chunk_files.append(chunk_path)
            except Exception as e:
                logger.warning(f"Failed to generate chunk {c_idx} in chapter {index}: {e}")

        if not chunk_files:
            logger.error(f"No audio chunks generated for chapter {index}")
            return None

        # 3. Combination (AIFFs -> Master AIFF)
        master_aiff = chapter_temp_dir / "combined_master.aiff"
        self.combiner.combine(chunk_files, master_aiff)

        # 4. Conversion (Master AIFF -> MP3/M4B)
        # Naming convention: "01 - Chapter Title.mp3"
        safe_title = "".join(c for c in chapter.title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{index:02d} - {safe_title}.{self.format}"
        final_path = self.output_dir / filename
        
        if self.format == "m4b":
             self.converter.to_m4b([master_aiff], final_path)
        else:
             self.converter.to_mp3(master_aiff, final_path)

        return final_path

    def _chunk_text(self, text: str, max_chars: int = 1000) -> List[str]:
        """
        Split text into smaller chunks safe for TTS generation.
        Splits by paragraph/newline first to preserve pause logic.
        """
        # Basic implementation: Split by double newline (paragraphs) first
        paragraphs = text.split('\n\n')
        chunks = []
        
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            
            # If paragraph is too long, split by period
            if len(p) > max_chars:
                sentences = p.split('. ')
                current_chunk = []
                current_len = 0
                for s in sentences:
                    # restore period if it's not the last one (approx)
                    s_clean = s + "." if not s.endswith('.') else s
                    if current_len + len(s_clean) > max_chars:
                        if current_chunk:
                            chunks.append(" ".join(current_chunk))
                        current_chunk = [s_clean]
                        current_len = len(s_clean)
                    else:
                        current_chunk.append(s_clean)
                        current_len += len(s_clean)
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
            else:
                chunks.append(p)
                
        return chunks
