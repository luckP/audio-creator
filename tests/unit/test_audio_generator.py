"""Unit tests for AudioGenerator."""
import unittest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.audio.generator import AudioGenerator

class TestAudioGenerator(unittest.TestCase):
    """Test cases for AudioGenerator."""

    def setUp(self):
        self.generator = AudioGenerator(voice="Samantha", rate=1.2)
        self.output_path = Path("test_output/audio.aiff")

    @patch("subprocess.run")
    def test_generate_chunk_success(self, mock_run):
        """Test successful audio generation."""
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        
        text = "Hello world."
        with patch("pathlib.Path.mkdir"): # Mock mkdir to avoid FS operations
            result = self.generator.generate_chunk(text, self.output_path)
        
        self.assertEqual(result, self.output_path)
        
        # Verify call arguments
        # Expected WPM: 180 * 1.2 = 216
        expected_cmd = [
            "say",
            "-v", "Samantha",
            "-r", "216",
            "-o", str(self.output_path),
            "--",
            text
        ]
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], expected_cmd)
        self.assertTrue(kwargs.get('check'))

    @patch("subprocess.run")
    def test_generate_chunk_failure(self, mock_run):
        """Test handling of subprocess failure."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=[], stderr="Voice not found"
        )
        
        with patch("pathlib.Path.mkdir"):
            with self.assertRaises(RuntimeError) as cm:
                self.generator.generate_chunk("Test", self.output_path)
            
        self.assertIn("Audio generation failed", str(cm.exception))

    @patch("subprocess.run")
    def test_generate_empty_text(self, mock_run):
        """Test that empty text skips generation."""
        result = self.generator.generate_chunk("   ", self.output_path)
        
        # Should return path but NOT call subprocess
        self.assertEqual(result, self.output_path)
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_command_not_found(self, mock_run):
        """Test when 'say' command is missing."""
        mock_run.side_effect = FileNotFoundError("No such file or directory")
        
        with patch("pathlib.Path.mkdir"):
            with self.assertRaises(RuntimeError) as cm:
                self.generator.generate_chunk("Test", self.output_path)
        
        self.assertIn("System command 'say' not found", str(cm.exception))
