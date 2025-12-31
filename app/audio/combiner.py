"""
Audio combiner module wrapping SoX (Sound eXchange).
"""
import subprocess
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class AudioCombiner:
    """
    Handles combining multiple audio files into a single track.
    Uses 'sox' command line tool.
    """

    def combine(self, input_files: List[Path], output_file: Path) -> Path:
        """
        Combine multiple input audio files into one output file.

        Args:
            input_files: List of paths to input files (e.g. AIFF chunks).
            output_file: Destination path for the combined audio.

        Returns:
            Path to the output file.
        
        Raises:
            RuntimeError: If inputs are invalid or sox command fails.
        """
        if not input_files:
            raise ValueError("No input files provided for combining.")

        if len(input_files) == 1:
            # Optimization: If only one file, just copy/move it? 
            # Or run through sox to ensure format consistency?
            # Let's run through sox to be safe about headers.
            pass

        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Construct command
        # sox input1.aiff input2.aiff ... output.aiff
        cmd = ["sox"] + [str(f) for f in input_files] + [str(output_file)]

        logger.debug(f"Combining {len(input_files)} files into {output_file}")

        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            error_msg = f"Audio combination failed: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except FileNotFoundError as e:
             error_msg = "System command 'sox' not found. Please install SoX (e.g., 'brew install sox')."
             logger.error(error_msg)
             raise RuntimeError(error_msg) from e

        return output_file
