---
date: 2026-01-01
status: implemented
---

# Implementation Plan: Audiobook Creator Enhancements

This document outlines the changes required to address issues with database persistence, chapter detection, and voice generation options.

## 1. Objectives

1.  **Fix Database Persistence**: Ensure document and chapter data is correctly saved to the content database.
2.  **Improve Chapter Detection**: Expand detection logic to identify all chapters/sections, not just the first one.
3.  **Add Microsoft Edge TTS**: Integrate generic/free high-quality voices from Microsoft Edge.

## 2. Technical Analysis & Implementation Steps

### A. Database Persistence Fix
**Problem**: The database tables (`documents`, `chapters`) remain empty after running the application.
**Root Cause**: The `app.py` script parses content and utilizes the database models for type hinting but never explicitly instantiates the database session or commits the objects to the database.
**Plan**:
1.  **Initialize DB**: Call `init_database()` in `app.py` before processing.
2.  **Persist Objects**:
    -   After successfully parsing `document` and detecting `chapters`:
    -   Create a `Document` ORM object.
    -   Iterate through chapters and create `Chapter` ORM objects linked to the document.
    -   Commit changes using a database session.
3.  **Update Status**: Update the document status to `completed` after audio generation is successful.

### B. Enhanced Chapter Detection
**Problem**: The system identifies the first chapter but fails to detect subsequent ones.
**Root Cause**: The regex patterns in `StructureDetector` are likely too strict or limited, failing to catch variations like "Part 1", Roman numerals on their own, or named sections (e.g., "Epilogue").
**Plan**:
1.  **Expand Regex Patterns**:
    -   Add patterns for: `Part X`, `Book X`, `Section X`.
    -   Add strict standalone number checks (e.g., `^/d+$` or `^[IVX]+$`) if they appear on their own lines.
    -   Add named section headers: `Preface`, `Prologue`, `Epilogue`, `Introduction`.
2.  **Preserve Structure**: Ensure the structure detector continues scanning the full text even after finding the first match. (Review `split_into_chapters` logic).

### C. Microsoft Edge TTS Integration
**Problem**: The user wants to use free, high-quality voices from Microsoft Edge.
**Root Cause**: The current `AudioGenerator` only supports the macOS `say` command.
**Plan**:
1.  **Dependencies**: Note that `edge-tts` (Python package) and `ffmpeg` (CLI tool) are required.
2.  **Modify `AudioGenerator`**:
    -   Add a check in `generate_chunk` for voice names containing "edge" or "neural".
    -   Implement a `_generate_edge_tts` helper method.
    -   Use `subprocess` to call `edge-tts` CLI to generate an MP3.
    -   Use `ffmpeg` to convert the MP3 to AIFF (to maintain compatibility with the pipeline's expected format).
    -   Clean up intermediate MP3 files.

## 3. Verification Strategy

1.  **Database**: Run the script and inspect `audiobooks.db` using `sqlite3` or a DB viewer to confirm rows exist in `documents` and `chapters`.
2.  **Detection**: Run with a complex text file (containing "Chapter 1", "II", "Epilogue") and verify the CLI summary output lists all sections.
3.  **Audio**: Run with `--voice edge` and listen to the output files to confirm correct voice and format.

## 4. Dependencies
-   `edge-tts` (Install via `pip install edge-tts`)
-   `ffmpeg` (Install via system package manager, e.g., `brew install ffmpeg`)
