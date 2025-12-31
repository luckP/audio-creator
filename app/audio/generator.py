"""
Audio generator module wrapping system TTS engine (macOS 'say').
"""
import subprocess
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

class AudioGenerator:
    """
    Handles generation of audio from text using system TTS.
    Currently supports macOS 'say' command.
    """

    def __init__(self, voice: str = "Alex", rate: float = 1.0):
        """
        Initialize the generator.

        Args:
            voice: Name of the system voice to use (default: "Alex").
            rate: Speech rate multiplier (default: 1.0).
                  Note: 'say' command rate is essentially words per minute? 
                  Actually 'say' uses -r with words per minute.
                  Standard roughly 175-200. We'll map 1.0 -> 180 wpm for now.
        """
        self.voice = voice
        self.rate = rate
        # Base WPM for rate=1.0
        self.base_wpm = 180 

    def generate_chunk(self, text: str, output_file: Path) -> Path:
        """
        Generate an AIFF audio file for the given text chunk.

        Args:
            text: The text content to speak.
            output_file: Path where the audio file should be saved.

        Returns:
            Path to the generated file.
        
        Raises:
            RuntimeError: If the generation command fails.
        """
        if not text.strip():
            logger.warning("Empty text chunk provided, skipping generation.")
            return output_file

        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate WPM
        wpm = int(self.base_wpm * self.rate)

        # Construct command
        # say -v "Voice" -r WPM -o "output.aiff" "text"
        cmd = [
            "say",
            "-v", self.voice,
            "-r", str(wpm),
            "-o", str(output_file),
            "--",  # End of options, treating next arg as text input
            text
        ]

        logger.debug(f"Generating audio: {cmd[:-1]} [Text Length: {len(text)}]")

        try:
            # Check if 'say' exists (sanity check for non-macOS dev environments)
            # In production this might be different, but for this project context (macOS) it's expected.
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            error_msg = f"Audio generation failed: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except FileNotFoundError as e:
             # If 'say' is missing
             error_msg = "System command 'say' not found. This application requires macOS or a compatible 'say' implementation."
             logger.error(error_msg)
             raise RuntimeError(error_msg) from e

        return output_file
