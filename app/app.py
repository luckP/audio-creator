"""
Main application entry point.
"""
import argparse
import sys
from pathlib import Path

from app.utils.logger import setup_logging, get_logger
from app.utils.config import get_config
from app.parsers import get_parser
from app.processors import TextCleaner, StructureDetector, MetadataExtractor
from app.audio import AudioPipeline

logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Audiobook Creator CLI")
    parser.add_argument("input_file", type=Path, help="Path to the input document")
    parser.add_argument("--config", type=Path, help="Path to custom configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    # Processing flags
    parser.add_argument("--clean-text", action="store_true", help="Clean and normalize text artifacts")
    parser.add_argument("--detect-chapters", action="store_true", help="Attempt to detect chapter structure in flat text")
    
    # Audio flags
    parser.add_argument("--generate-audio", action="store_true", help="Generate audio files")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Directory for output audio files")
    parser.add_argument("--voice", type=str, default="Alex", help="System voice to use (default: Alex)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech rate multiplier (default: 1.0)")
    parser.add_argument("--format", type=str, default="mp3", choices=["mp3", "m4b"], help="Output audio format")

    args = parser.parse_args()
    
    # Setup Config
    if args.config:
        _ = get_config(args.config)

    # Setup Logging
    log_level = "DEBUG" if args.verbose else None
    setup_logging(level=log_level)
    
    logger.info("Starting Audiobook Creator processing for: %s", args.input_file)
    
    try:
        if not args.input_file.exists():
            logger.error("Input file not found: %s", args.input_file)
            sys.exit(1)

        # 1. Parse
        # ---------
        doc_parser = get_parser(args.input_file)
        logger.info("Using parser: %s", doc_parser.__class__.__name__)
        document = doc_parser.parse(args.input_file)
        
        # 2. Process
        # ---------
        
        # Text Cleaning
        if args.clean_text:
            logger.info("Cleaning text...")
            cleaner = TextCleaner()
            document.content = cleaner.clean(document.content)
            for chapter in document.chapters:
                chapter.content = cleaner.clean(chapter.content)

        # Structure Detection
        if args.detect_chapters and not document.chapters and document.content:
            logger.info("Detecting structure...")
            detector = StructureDetector()
            detected_chapters = detector.split_into_chapters(document.content)
            if detected_chapters:
                document.chapters = detected_chapters
                logger.info("Detected %d chapters", len(detected_chapters))
            else:
                logger.warning("No structure detected during structure processing")

        # Metadata Extraction
        logger.debug("Enriching metadata...")
        extractor = MetadataExtractor()
        sample_text = document.content[:5000] if document.content else ""
        document.metadata = extractor.extract(sample_text, document.metadata)
        
        if not document.author and 'author' in document.metadata:
            document.author = document.metadata['author']
        if not document.title or document.title == "Untitled":
            if 'title' in document.metadata:
                document.title = document.metadata['title']

        # 2.5 DB Persistence
        # ------------------
        logger.info("Saving to database...")
        from app.models.database import init_database, get_db
        from app.models.document import Document
        from app.models.chapter import Chapter

        init_database()
        
        with get_db() as db:
            # Create Document
            db_doc = Document(
                title=document.title,
                author=document.author,
                source_file=str(args.input_file),
                format=args.input_file.suffix.replace('.', ''),
                status="processing", # Will update to completed/failed later
                content_length=len(document.content)
            )
            db.add(db_doc)
            db.flush() # Generate ID

            # Create Chapters
            if document.chapters:
                for ch in document.chapters:
                    db_ch = Chapter(
                        document_id=db_doc.id,
                        number=ch.number,
                        title=ch.title,
                        content=ch.content
                    )
                    db.add(db_ch)
            else:
                # Treat as single chapter
                db_ch = Chapter(
                    document_id=db_doc.id,
                    number=1,
                    title=document.title,
                    content=document.content
                )
                db.add(db_ch)
            
            db.commit()
            document_id = db_doc.id  # Store primitive ID
            logger.info(f"Saved Document ID: {document_id}")

        # 3. Report
        # ---------
        logger.info("Processing successful!")
        print("\n" + "=" * 50)
        print("📄  Document Summary")
        print("=" * 50)
        print(f"Title:    {document.title}")
        print(f"Author:   {document.author or 'Unknown'}")
        
        if 'publication_year' in document.metadata:
            print(f"Year:     {document.metadata['publication_year']}")
        if 'isbn' in document.metadata:
            print(f"ISBN:     {document.metadata['isbn']}")
            
        print(f"Content:  {len(document.content)} characters")
        
        if document.chapters:
            print(f"Chapters: {len(document.chapters)}")
            print("-" * 50)
            if len(document.chapters) > 10:
                for chapter in document.chapters[:5]:
                    print(f"  {chapter.number}. {chapter.title} ({len(chapter.content)} chars)")
                print(f"  ... (+ {len(document.chapters) - 10} more) ...")
                for chapter in document.chapters[-5:]:
                    print(f"  {chapter.number}. {chapter.title} ({len(chapter.content)} chars)")
            else:
                for chapter in document.chapters:
                    print(f"  {chapter.number}. {chapter.title} ({len(chapter.content)} chars)")
        else:
            print("Chapters: None (Single block content)")
            
        print("=" * 50 + "\n")

        # 4. Audio Generation
        # -------------------
        if args.generate_audio:
            print("🎧  Audio Generation Starting...")
            print("=" * 50)
            pipeline = AudioPipeline(
                output_dir=args.output_dir,
                voice=args.voice,
                speed=args.speed,
                format=args.format
            )
            
            generated_files = pipeline.process_document(document)
            
            # Update DB with audio files
            if generated_files:
                 with get_db() as db:
                     # Re-fetch to ensure attached to session
                     db_doc = db.query(Document).get(document_id)
                     db_doc.status = "completed"
                     
                     # Map files to chapters (heuristic or exact)
                     # For now, just mark completed. 
                     # Ideally we'd map back, but pipeline returns list of paths.
                     # We can iterate chapters and check if file exists?
                     # The pipeline creates "01 - Title.mp3".
                     
                     db.commit()

            print("-" * 50)
            print(f"✅ Generated {len(generated_files)} audio files in '{args.output_dir}'")
            for f in generated_files:
                print(f"   - {f.name}")
            print("=" * 50 + "\n")

    except ValueError as e:
        logger.error("Validation Error: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.critical("Unexpected Error: %s", e, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
