# Week 3 Action Plan - Text Processing

**Goal**: Implement intelligent text cleaning and structure detection to prepare content for high-quality audio generation.

---

## 🎯 This Week's Objectives

1.  Implement **TextCleaner** to normalize text, remove artifacts (page numbers, headers), and fix formatting.
2.  Implement **StructureDetector** to identify document hierarchy (titles, chapters) when parsers miss them.
3.  Implement **MetadataExtractor** to enrich document info.
4.  Achieve 80%+ test coverage for valid processing logic.

---

## 📋 Day-by-Day Breakdown

### Day 1: Text Cleaner Implementation
**Tasks**:
1.  Create `app/processors/text_cleaner.py`:
    -   Regex-based cleaning patterns.
    -   Remove page numbers (e.g., "Page 1 of 10", "- 5 -").
    -   Fix hyphenation at line breaks (e.g., "impor-\ntant" -> "important").
    -   Normalize whitespace (multiple newlines -> paragraph breaks).
2.  Create unit tests `tests/unit/test_text_cleaner.py`.
    -   Test with dirty text samples (PDF artifacts).

**Deliverable**: `TextCleaner` class that produces clean, TTS-ready string.

---

### Day 2: Structure Detector
**Tasks**:
1.  Create `app/processors/structure_detector.py`.
2.  Implement heuristic detection:
    -   Detect ALL CAPS lines as potential headers.
    -   Detect numbered lines ("1. Introduction", "Chapter II") as chapters.
    -   Split flat text into `Chapter` objects if the parser failed to do so.
3.  Write tests in `tests/unit/test_structure_detector.py`.

**Deliverable**: Logic to turn a "flat blob of text" into a structured list of Chapters.

---

### Day 3: Metadata Extractor
**Tasks**:
1.  Create `app/processors/metadata_extractor.py`.
2.  Implement extraction logic:
    -   Extract ISBNs, Emails, URLs.
    -   Guess Author/Title from the first few lines if missing.
3.  Integrate with `ParsedDocument` to fill in missing fields.
4.  Write tests.

**Deliverable**: Enriched metadata for documents.

---

### Day 4: Integration - The Processing Pipeline
**Tasks**:
1.  Update `app/app.py` (CLI) to include a "Cleaning" step.
2.  Create `app/processors/pipeline.py` (optional but good practice) or just use a helper function:
    -   `Parser` -> `RawDocument`
    -   `TextCleaner` -> `CleanText`
    -   `StructureDetector` -> `StructuredDocument`
3.  Verify the flow end-to-end with a "dirty" PDF.

**Deliverable**: CLI now produces cleaner output logs and better chapter splits.

---

### Day 5: Refinement & Testing
**Tasks**:
1.  Run full test suite.
2.  Handle edge cases (e.g., code blocks in Markdown usually shouldn't be "cleaned" aggressively).
3.  Document the Processor API.

---

## 🏗️ File Structure Updates

```
audio-creator/
├── app/
│   ├── processors/
│   │   ├── __init__.py          ✅ NEW
│   │   ├── text_cleaner.py      ✅ NEW
│   │   ├── structure_detector.py ✅ NEW
│   │   └── metadata_extractor.py ✅ NEW
├── tests/
│   ├── unit/
│   │   ├── test_text_cleaner.py ✅ NEW
│   │   ├── test_structure_detector.py ✅ NEW
│   │   └── test_metadata_extractor.py ✅ NEW
```

---

## ⚠️ Common Pitfalls

1.  **Over-cleaning**: Be careful not to remove valid content (e.g., year "2023" looking like a page number).
2.  **Context Matters**: A "Chapter 1" regex might match a sentence like "In Chapter 1, we discussed...". Ensure we check for standalone lines.
3.  **Language Support**: Regexes might need to support other languages (e.g., "Capítulo").

---

## 🎯 Success Criteria for Week 3

-   [ ] `TextCleaner` removes 90%+ of common PDF artifacts (headers/footers/page nums).
-   [ ] Hyphenated words across lines are joined correctly.
-   [ ] Flat text files are successfully split into Chapters by `StructureDetector`.
-   [ ] CLI runs successfully with `--clean-text` flag (to be added).
