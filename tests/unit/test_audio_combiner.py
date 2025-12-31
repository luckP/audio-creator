"""Unit tests for AudioCombiner."""
import unittest
import subprocess
from pathlib import Path
from unittest.mock import patch

from app.audio.combiner import AudioCombiner

class TestAudioCombiner(unittest.TestCase):
    """Test cases for AudioCombiner."""

    def setUp(self):
        self.combiner = AudioCombiner()
        self.inputs = [Path("part1.aiff"), Path("part2.aiff")]
        self.output = Path("combined.aiff")

    @patch("subprocess.run")
    def test_combine_success(self, mock_run):
        """Test successful combination."""
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        
        with patch("pathlib.Path.mkdir"):
            result = self.combiner.combine(self.inputs, self.output)
            
        self.assertEqual(result, self.output)
        
        expected_cmd = ["sox", "part1.aiff", "part2.aiff", "combined.aiff"]
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        self.assertEqual(args[0], expected_cmd)

    def test_no_inputs(self):
        """Test error when no inputs provided."""
        with self.assertRaises(ValueError):
             self.combiner.combine([], self.output)

    @patch("subprocess.run")
    def test_sox_not_found(self, mock_run):
        """Test failure when sox is missing."""
        mock_run.side_effect = FileNotFoundError("sox not found")
        
        with patch("pathlib.Path.mkdir"):
            with self.assertRaises(RuntimeError) as cm:
                self.combiner.combine(self.inputs, self.output)
        
        self.assertIn("System command 'sox' not found", str(cm.exception))
