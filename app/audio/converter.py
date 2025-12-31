"""
Audio converter module wrapping FFmpeg.
"""
import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class AudioConverter:
    """
    Handles conversion of audio files using FFmpeg.
    """

    def to_mp3(self, input_file: Path, output_file: Path, bitrate: str = "192k") -> Path:
        """
        Convert input audio to MP3 format.

        Args:
            input_file: Path to source audio.
            output_file: Path for destination MP3.
            bitrate: Audio bitrate (default: "192k").

        Returns:
            Path to the output file.
        
        Raises:
            RuntimeError: If ffmpeg fails.
        """
        self._ensure_ffmpeg_installed()
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # ffmpeg -y -i input.aiff -codec:a libmp3lame -b:a 192k output.mp3
        cmd = [
            "ffmpeg",
            "-y",          # Overwrite output files
            "-i", str(input_file),
            "-codec:a", "libmp3lame",
            "-b:a", bitrate,
            str(output_file)
        ]

        logger.debug(f"Converting to MP3: {input_file} -> {output_file}")
        self._run_command(cmd, "MP3 conversion failed")
        
        return output_file

    def to_m4b(self, input_files: List[Path], output_file: Path, metadata: Optional[Dict[str, str]] = None) -> Path:
        """
        Convert/Combine multiple files into an M4B audiobook (AAC encoding).
        
        Note: For M4B with chapter marks, we usually need a complex metadata file or specific ffmpeg inputs.
        For this v1, we will simple concatenate and convert to M4B/AAC if given a single file (usually we combine first).
        If multiple files are given, we use the concat demuxer.

        Args:
            input_files: List of input audio files.
            output_file: Path for destination M4B.
            metadata: Optional metadata (Title, Author, etc.).

        Returns:
            Path to the output file.
        """
        self._ensure_ffmpeg_installed()
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 1. Create a temporary file list for ffmpeg concat demuxer
        # format: file '/path/to/file'
        concat_list_path = output_file.parent / "concat_list.txt"
        with open(concat_list_path, 'w', encoding='utf-8') as f:
            for path in input_files:
                # Escape single quotes in path
                safe_path = str(path.absolute()).replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")

        # 2. Build command
        # ffmpeg -y -f concat -safe 0 -i list.txt -c:a aac -b:a 128k output.m4b
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_path),
            "-c:a", "aac",
            "-b:a", "128k",
            str(output_file)
        ]
        
        # Add metadata inputs? (TODO for refinement step)
        
        logger.debug(f"Creating M4B from {len(input_files)} files.")
        try:
            self._run_command(cmd, "M4B creation failed")
        finally:
            # Cleanup list file
            if concat_list_path.exists():
                concat_list_path.unlink()

        return output_file

    def _run_command(self, cmd: List[str], error_prefix: str):
        """Helper to run subprocess."""
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            error_msg = f"{error_prefix}: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _ensure_ffmpeg_installed(self):
        """Check if FFmpeg is available."""
        # This could check `which ffmpeg` or just fail lazily.
        # We assume it is handled by the caller or environment for now.
        pass
