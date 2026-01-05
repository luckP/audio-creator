"""
Audio generator module wrapping system TTS engine (macOS 'say').
"""
import subprocess
import logging
import shutil
import sys
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

class AudioGenerator:
    """
    Handles generation of audio from text using system TTS.
    Currently supports macOS 'say' command.
    """

    def __init__(self, voice: Optional[str] = None, rate: float = 1.0):
        """
        Initialize the generator.

        Args:
            voice: Name of the system voice to use.
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

        if self.voice and (self.voice.lower() == "edge" or "neural" in self.voice.lower()):
             return self._generate_edge_tts(text, output_file)

        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate WPM
        wpm = int(self.base_wpm * self.rate)

        # Construct command
        # say [-v Voice] -r WPM -o "output.aiff" "text"
        cmd = ["say"]
        
        if self.voice:
             cmd.extend(["-v", self.voice])

        cmd.extend([
            "-r", str(wpm),
            "-o", str(output_file),
            "--",  # End of options, treating next arg as text input
            text
        ])

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

    def _generate_edge_tts(self, text: str, output_file: Path) -> Path:
        """
        Generate audio using edge-tts CLI.
        Requires 'edge-tts' and 'ffmpeg' (for conversion to AIFF) to be installed.
        """
        # Default voice if just "edge" specified
        voice = self.voice if self.voice != "edge" else "en-US-AriaNeural"
        
        # rate string for edge-tts: "+0%" or "+50%" etc.
        # self.rate 1.0 -> +0%, 1.5 -> +50%
        rate_pct = int((self.rate - 1.0) * 100)
        rate_str = f"{rate_pct:+d}%"
        
        # Intermediate MP3 file
        temp_mp3 = output_file.with_suffix(".mp3")
        
        # Find 'edge-tts' executable
        edge_executable = shutil.which("edge-tts")
        if not edge_executable:
            # Fallback for venv: check if it's in the same bin as python
            venv_bin = Path(sys.executable).parent
            candidate = venv_bin / "edge-tts"
            if candidate.exists():
                edge_executable = str(candidate)
            else:
                 # Last resort: try running as module "python -m edge_tts"
                 # NOTE: This requires changing the command structure entirely. 
                 # Let's hope finding the binary works.
                 pass
        
        if not edge_executable:
             # Default to just command name and hope for the best
             edge_executable = "edge-tts"

        cmd = [
            edge_executable,
            "--voice", voice,
            "--rate", rate_str,
            "--text", text,
            "--write-media", str(temp_mp3)
        ]
        
        try:
            # 1. Generate MP3
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # 2. Convert to AIFF (pipeline expects AIFF)
            # ffmpeg -i input.mp3 -f aiff output.aiff
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(temp_mp3), "-f", "aiff", str(output_file)],
                check=True,
                capture_output=True,
                text=True
            )
            
            # Cleanup temp MP3
            if temp_mp3.exists():
                temp_mp3.unlink()
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Edge TTS generation failed: {e}")
            raise RuntimeError(f"Edge TTS failed. Ensure 'edge-tts' and 'ffmpeg' are installed. Error: {e}") from e
            
        return output_file
