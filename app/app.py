"""
Main application entry point.
"""
import argparse
import sys
from pathlib import Path

from app.utils.logger import setup_logging, get_logger
from app.utils.config import get_config
from app.parsers import get_parser

logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Audiobook Creator CLI")
    parser.add_argument("input_file", type=Path, help="Path to the input document")
    parser.add_argument("--config", type=Path, help="Path to custom configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup Config
    if args.config:
        # Load custom config using the global accessor if possible, or re-initialize
        # For now, we'll just reload the global config manager with the new path
        # A cleaner approach would be 'get_config(config_path)' but it's a singleton pattern
        # inside config.py we can call get_config(args.config) which initializes it if not set,
        # but if it was already set (e.g. by imports?), we might need to force reload.
        # Since this is main(), it's the first time we call it.
        _ = get_config(args.config)

    # Setup Logging
    log_level = "DEBUG" if args.verbose else None
    setup_logging(level=log_level)
    
    logger.info("Starting Audiobook Creator processing for: %s", args.input_file)
    
    try:
        if not args.input_file.exists():
            logger.error("Input file not found: %s", args.input_file)
            sys.exit(1)

        # Get Parser
        doc_parser = get_parser(args.input_file)
        logger.info("Using parser: %s", doc_parser.__class__.__name__)
        
        # Parse
        document = doc_parser.parse(args.input_file)
        
        # Report
        logger.info("Parsing successful!")
        print("\n" + "=" * 50)
        print("📄  Document Summary")
        print("=" * 50)
        print(f"Title:    {document.title}")
        print(f"Author:   {document.author or 'Unknown'}")
        
        print(f"Content:  {len(document.content)} characters")
        
        if document.chapters:
            print(f"Chapters: {len(document.chapters)}")
            print("-" * 50)
            for chapter in document.chapters:
                print(f"  {chapter.number}. {chapter.title} ({len(chapter.content)} chars)")
        else:
            print("Chapters: None (Single block content)")
            
        print("=" * 50 + "\n")

    except ValueError as e:
        logger.error("Validation Error: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.critical("Unexpected Error: %s", e, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
