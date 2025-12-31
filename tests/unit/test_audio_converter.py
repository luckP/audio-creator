"""Unit tests for AudioConverter."""
import unittest
import subprocess
from pathlib import Path
from unittest.mock import patch, mock_open

from app.audio.converter import AudioConverter

class TestAudioConverter(unittest.TestCase):
    """Test cases for AudioConverter."""

    def setUp(self):
        self.converter = AudioConverter()
        self.input_file = Path("input.aiff")
        self.output_mp3 = Path("output.mp3")
        self.output_m4b = Path("output.m4b")

    @patch("subprocess.run")
    def test_to_mp3_success(self, mock_run):
        """Test successful MP3 conversion."""
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        
        with patch("pathlib.Path.mkdir"):
            result = self.converter.to_mp3(self.input_file, self.output_mp3)

        self.assertEqual(result, self.output_mp3)
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        self.assertIn("ffmpeg", args[0])
        self.assertIn("libmp3lame", args[0])

    @patch("subprocess.run")
    def test_to_m4b_success(self, mock_run):
        """Test successful M4B conversion with concat."""
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        inputs = [Path("part1.aiff"), Path("part2.aiff")]
        
        with patch("pathlib.Path.mkdir"), \
             patch("builtins.open", mock_open()) as mocked_file, \
             patch("pathlib.Path.unlink"): # Mock unlink to avoid Deleting real files if path existed
            
            result = self.converter.to_m4b(inputs, self.output_m4b)

        self.assertEqual(result, self.output_m4b)
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        self.assertIn("concat", args[0])
        self.assertIn("aac", args[0])

    @patch("subprocess.run")
    def test_conversion_failure(self, mock_run):
        """Test handling FFmpeg failure."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=[], stderr="Codec not found"
        )
        
        with patch("pathlib.Path.mkdir"):
            with self.assertRaises(RuntimeError) as cm:
                self.converter.to_mp3(self.input_file, self.output_mp3)
        
        self.assertIn("MP3 conversion failed", str(cm.exception))
