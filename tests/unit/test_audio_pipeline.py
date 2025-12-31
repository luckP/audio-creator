"""Unit tests for AudioPipeline."""
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from app.audio.pipeline import AudioPipeline
from app.parsers.base_parser import ParsedDocument, ParsedChapter

class TestAudioPipeline(unittest.TestCase):
    """Test cases for AudioPipeline."""

    def setUp(self):
        self.output_dir = Path("test_output")
        self.pipeline = AudioPipeline(output_dir=self.output_dir)
        
        # Mocks for components
        self.pipeline.generator = MagicMock()
        self.pipeline.combiner = MagicMock()
        self.pipeline.converter = MagicMock()

    @patch("tempfile.TemporaryDirectory")
    def test_process_document_single_chapter(self, mock_temp_dir):
        """Test processing a document with a single chapter."""
        # Setup temp dir context manager
        mock_temp_dir.return_value.__enter__.return_value = "/tmp/mock_audio"
        
        # Setup document
        doc = ParsedDocument(
            title="Test Book",
            content="Full Content", # Should be ignored if chapters exist
            chapters=[
                ParsedChapter(title="Chapter 1", content="Hello world.", number=1)
            ]
        )
        
        # Mock generator to simulate creating a file
        def side_effect_gen(text, path):
            # In a real scenario, this creates a file. 
            # We just return the path (as the real method does) 
            # but we need to ensure the pipeline thinks it exists if it checks .exists()
            return path
        self.pipeline.generator.generate_chunk.side_effect = side_effect_gen
        
        # Mock exists() checks inside pipeline
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.mkdir"):
            
            final_files = self.pipeline.process_document(doc)
            
        self.assertEqual(len(final_files), 1)
        
        # Check Generator called
        self.pipeline.generator.generate_chunk.assert_called()
        
        # Check Combiner called
        self.pipeline.combiner.combine.assert_called_once()
        
        # Check Converter called (MP3 default)
        self.pipeline.converter.to_mp3.assert_called_once()
        
        # Verify output filename format "01 - Chapter 1.mp3"
        args, _ = self.pipeline.converter.to_mp3.call_args
        output_path = args[1]
        self.assertIn("01 - Chapter 1.mp3", str(output_path))

    @patch("tempfile.TemporaryDirectory")
    def test_process_document_no_chapters(self, mock_temp_dir):
        """Test processing a document without specific chapters."""
        mock_temp_dir.return_value.__enter__.return_value = "/tmp/mock_audio"
        
        doc = ParsedDocument(
            title="Flat Book",
            content="Just some text content.",
            chapters=[]
        )
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.mkdir"):   
            final_files = self.pipeline.process_document(doc)
            
        self.assertEqual(len(final_files), 1)
        self.pipeline.converter.to_mp3.assert_called_once()
        
        # Should treat as Chapter 1
        args, _ = self.pipeline.converter.to_mp3.call_args
        self.assertIn("01 - Flat Book.mp3", str(args[1]))

    def test_chunk_text(self):
        """Test text chunking logic."""
        text = "Sentence one. Sentence two."
        chunks = self.pipeline._chunk_text(text, max_chars=100)
        # Should be one chunk if small enough
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)
        
        # Force split
        text_long = "A" * 60 + ". " + "B" * 60 + "."
        chunks = self.pipeline._chunk_text(text_long, max_chars=80)
        self.assertEqual(len(chunks), 2)
