"""
Audio Creator - Convert text files to audio using macOS 'say' command.

This script reads a text file, splits it into chunks, converts each chunk to AIFF
audio files using the macOS 'say' command, combines them into a single file,
and converts the result to MP3 format.

Requirements:
    - macOS (for 'say' command)
    - sox (for audio file concatenation)
    - ffmpeg (for MP3 conversion)

Usage:
    python main.py <input_text_file> [output_directory]
"""

import sys
import logging
from time import time
from pathlib import Path
from typing import Iterator, List
import subprocess

# Constants
LINES_PER_CHUNK = 50
TIMEOUT_SECONDS = 300

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def read_file(file_path: Path) -> Iterator[str]:
    """
    Read a text file and yield its contents line by line.

    Args:
        file_path (Path): Path to the file to read

    Yields:
        str: Each line from the file

    Raises:
        FileNotFoundError: If the file doesn't exist
        IsADirectoryError: If the path is a directory
        PermissionError: If the file cannot be read
    """
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            yield line


def split_file(file: Iterator[str], chunk_size: int = LINES_PER_CHUNK) -> Iterator[str]:
    """
    Split file content into groups of lines.

    Args:
        file (Iterator[str]): Iterator of lines from the file
        chunk_size (int): Number of lines per chunk (default: 50)

    Yields:
        str: Text groups, each containing up to chunk_size lines concatenated
    """
    lines: List[str] = []

    for i, line in enumerate(file):
        lines.append(line)
        if (i + 1) % chunk_size == 0:
            yield ''.join(lines)
            lines = []

    # Yield any remaining text that didn't complete a full group
    if lines:
        yield ''.join(lines)


def create_aiff_files(
    group_text: Iterator[str],
    output_dir: Path,
    timeout: int = TIMEOUT_SECONDS
) -> None:
    """
    Create AIFF audio files from text groups using macOS 'say' command.

    Args:
        group_text (Iterator[str]): Iterator of text strings to convert to audio
        output_dir (Path): Directory where AIFF files will be saved
        timeout (int): Timeout in seconds for each audio generation (default: 300)

    Note:
        Creates numbered AIFF files (0.aiff, 1.aiff, etc.) in the output directory.
        Retries on timeout and removes failed files.
        Creates output directory if it doesn't exist.

    Raises:
        RuntimeError: If audio generation fails repeatedly
    """
    # Try to create directory - will succeed if it exists or if we can create it
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise RuntimeError(f"Cannot create output directory {output_dir}: {e}") from e

    file_counter = 0  # Track actual files created (excluding skipped chunks)

    for i, text in enumerate(group_text):
        # Skip empty or whitespace-only chunks
        if not text.strip():
            logger.debug("Skipping empty text chunk at index %d", i)
            continue

        output_file = output_dir / f"{file_counter}.aiff"
        confirm = False
        retry_count = 0
        max_retries = 3

        while not confirm and retry_count < max_retries:
            process = subprocess.Popen(
                ['say', text, '-o', str(output_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            try:
                start_time = time()
                process.wait(timeout)
                elapsed_time = time() - start_time
                logger.info('File %d completed in %.2fs', file_counter, elapsed_time)
                confirm = True
            except subprocess.TimeoutExpired:
                # Kill the process and clean up
                process.kill()
                process.wait()  # Ensure process is terminated

                # Remove incomplete file if it exists
                try:
                    output_file.unlink()
                except FileNotFoundError:
                    pass  # File doesn't exist, nothing to clean up

                retry_count += 1
                logger.warning(
                    'Timeout on file %d (attempt %d/%d), retrying...',
                    file_counter, retry_count, max_retries
                )

        if not confirm:
            raise RuntimeError(
                f"Failed to create audio file {file_counter} after {max_retries} attempts"
            )

        file_counter += 1  # Increment only when file is successfully created


def combine_aiff_files(output_dir: Path, cleanup: bool = True) -> None:
    """
    Combine all numbered AIFF files in a directory into a single output file.

    Args:
        output_dir (Path): Directory containing AIFF files to combine
        cleanup (bool): If True, remove intermediate numbered files after combining (default: True)

    Raises:
        RuntimeError: If sox command fails
        FileNotFoundError: If no AIFF files are found
    """
    output_file = output_dir / "output.aiff"

    # Get all numbered AIFF files (0.aiff, 1.aiff, etc.), excluding output.aiff
    aiff_files = sorted([
        f for f in output_dir.glob("*.aiff")
        if f.name != "output.aiff" and f.stem.isdigit()
    ])

    if not aiff_files:
        raise FileNotFoundError(f"No AIFF files found in {output_dir}")

    # Build sox command with explicit file list
    cmd = ['sox'] + [str(f) for f in aiff_files] + [str(output_file)]

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Successfully created output file: %s", output_file)

        # Clean up intermediate files if requested
        if cleanup:
            for aiff_file in aiff_files:
                try:
                    aiff_file.unlink()
                    logger.debug("Removed intermediate file: %s", aiff_file)
                except OSError as e:
                    logger.warning("Failed to remove %s: %s", aiff_file, e)
            logger.info("Cleaned up %d intermediate files", len(aiff_files))

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to combine audio files: {e.stderr}") from e
    except FileNotFoundError:
        raise RuntimeError(
            "sox command not found. Please install sox: brew install sox"
        ) from None


def convert_to_mp3(output_dir: Path, keep_aiff: bool = False) -> None:
    """
    Convert the output AIFF file to MP3 format.

    Args:
        output_dir (Path): Directory containing the output.aiff file
        keep_aiff (bool): If True, keep the AIFF file after conversion (default: False)

    Raises:
        RuntimeError: If ffmpeg command fails
        FileNotFoundError: If output.aiff is not found
    """
    aiff_file = output_dir / "output.aiff"
    mp3_file = output_dir / "output.mp3"

    if not aiff_file.exists():
        raise FileNotFoundError(f"AIFF file not found: {aiff_file}")

    # Build ffmpeg command to convert AIFF to MP3
    # -i: input file
    # -codec:a libmp3lame: use LAME MP3 encoder
    # -qscale:a 2: quality scale (0-9, where 2 is high quality ~190 kbps)
    # -y: overwrite output file if it exists
    cmd = [
        'ffmpeg',
        '-i', str(aiff_file),
        '-codec:a', 'libmp3lame',
        '-qscale:a', '2',
        '-y',
        str(mp3_file)
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Successfully converted to MP3: %s", mp3_file)

        # Remove AIFF file if requested
        if not keep_aiff:
            try:
                aiff_file.unlink()
                logger.info("Removed AIFF file: %s", aiff_file)
            except OSError as e:
                logger.warning("Failed to remove AIFF file %s: %s", aiff_file, e)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to convert to MP3: {e.stderr}") from e
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg command not found. Please install ffmpeg: brew install ffmpeg"
        ) from None


def main(argv: List[str]) -> None:
    """
    Main entry point for the audio creator application.

    Args:
        argv (List[str]): Command line arguments
            argv[1]: Path to input text file
            argv[2]: Path to output directory (optional, defaults to input file's directory)

    Raises:
        SystemExit: If invalid arguments are provided or an error occurs
    """
    if len(argv) < 2:
        sys.exit(
            "Usage: python main.py <input_text_file> [output_directory]\n"
            "Example: python main.py input.txt ./output/"
        )

    # Parse arguments
    input_file = Path(argv[1])

    if len(argv) >= 3:
        output_dir = Path(argv[2])
    else:
        # Default to a subdirectory next to the input file
        output_dir = input_file.parent / f"{input_file.stem}_audio"

    try:
        logger.info("Starting audio creation from: %s", input_file)
        logger.info("Output directory: %s", output_dir)

        # Process the file
        file_lines = read_file(input_file)
        group_text = split_file(file_lines)
        create_aiff_files(group_text, output_dir)
        combine_aiff_files(output_dir, cleanup=True)
        convert_to_mp3(output_dir, keep_aiff=False)

        logger.info("Audio creation finished successfully")
        logger.info("Output file: %s", output_dir / 'output.mp3')

    except FileNotFoundError as e:
        logger.error("File error: %s", e)
        sys.exit(1)
    except IsADirectoryError:
        logger.error("Input path is a directory, not a file: %s", input_file)
        sys.exit(1)
    except PermissionError as e:
        logger.error("Permission denied: %s", e)
        sys.exit(1)
    # except ValueError as e:
    #     logger.error("Invalid input: %s", e)
    #     sys.exit(1)
    except RuntimeError as e:
        logger.error("Runtime error: %s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(130)
    except Exception as e:  # pylint: disable=broad-except
        # Final catch-all for any unexpected errors - we want to log and exit gracefully
        logger.error("Unexpected error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
