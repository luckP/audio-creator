# Week 2 Action Plan - Document Parsers

**Goal**: Extend the system to support rich document formats (PDF, Markdown, EPUB) by implementing specialized parsers.

---

## 🎯 This Week's Objectives

1.  Implement `PDFParser` for intelligent text extraction from PDFs.
2.  Implement `MarkdownParser` with structure preservation (headers as chapters).
3.  Implement `EpubParser` for parsing electronic books.
4.  Standardize the output of all parsers into the `Document` / `Chapter` model.
5.  Achieve 80%+ test coverage for new parsers.

---

## 📋 Day-by-Day Breakdown

### Day 1: PDF Parser Implementation
**Tasks**:
1.  Install dependencies:
    ```bash
    pip install pdfplumber
    pip freeze > requirements.txt
    ```
2.  Create `app/parsers/pdf_parser.py`:
    -   Inherit from `BaseParser`.
    -   Use `pdfplumber` to extract text.
    -   Implement basic logic to ignore headers/footers (configurable).
    -   **Challenge**: PDFs are messy. Focus on extraction first, perfect structure later.
3.  Register the parser in `app/parsers/__init__.py`.
4.  Create test file `tests/fixtures/sample.pdf` (or use a mock).

**Deliverable**: Working `PDFParser` that extracts clean text.

---

### Day 2: PDF Parser Testing & Refinement
**Tasks**:
1.  Write tests in `tests/unit/test_pdf_parser.py`.
2.  Handle edge cases:
    -   Encrypted PDFs (fail gracefully).
    -   Image-only PDFs (OCR is out of scope for now, just informative error).
    -   Multi-column layouts (basic support).
3.  Refine text extraction:
    -   Attempt to detect titles/chapters based on font size (introductory heuristic).

**Deliverable**: Robust `PDFParser` with solid test coverage.

---

### Day 3: Markdown Parser
**Tasks**:
1.  Install dependencies:
    ```bash
    pip install markdown
    # (Update requirements.txt)
    ```
2.  Create `app/parsers/markdown_parser.py`:
    -   This is easier than PDF!
    -   Use the structure to our advantage: `# Heading 1` = Title, `## Heading 2` = Chapter.
    -   Extract metadata from Front Matter (YAML style) if present.
3.  Register in `app/parsers/__init__.py`.
4.  Write tests in `tests/unit/test_markdown_parser.py`.

**Deliverable**: `MarkdownParser` that auto-detects chapters based on headers.

---

### Day 4: EPUB Parser
**Tasks**:
1.  Install dependencies:
    ```bash
    pip install EbookLib
    # (Update requirements.txt)
    ```
2.  Create `app/parsers/epub_parser.py`:
    -   Inherit from `BaseParser`.
    -   Iterate through spinal items (chapters).
    -   Use `BeautifulSoup` (likely needed) to strip HTML tags from content.
    -   Extract rich metadata (cover image path, author, ISBN).
3.  Register in `app/parsers/__init__.py`.

**Deliverable**: `EpubParser` that converts an ebook into our standard `Document` model.

---

### Day 5: EPUB Testing & Integration
**Tasks**:
1.  Write tests in `tests/unit/test_epub_parser.py`.
2.  Integration Check:
    -   Update `app/app.py` to ensure CLI flags work with these new parsers (e.g., verifying `get_parser` automatically picks the right one).
    -   Verify that all parsers output a valid `Document` object that can be saved to the database.

**Deliverable**: All parsers integrated and working with the CLI entry point.

---

## 🏗️ File Structure Updates

```
audio-creator/
├── app/
│   ├── parsers/
│   │   ├── pdf_parser.py        ✅ NEW
│   │   ├── markdown_parser.py   ✅ NEW
│   │   └── epub_parser.py       ✅ NEW
├── tests/
│   ├── fixtures/
│   │   ├── sample.pdf           ✅ NEW
│   │   ├── sample.md            ✅ NEW
│   │   └── sample.epub          ✅ NEW
│   └── unit/
│       ├── test_pdf_parser.py   ✅ NEW
│       ├── test_markdown_parser.py ✅ NEW
│       └── test_epub_parser.py  ✅ NEW
```

---

## ⚠️ Common Pitfalls to Avoid

1.  **PDF Complexity**: Don't try to build a perfect PDF parser overnight. It's an entire project in itself. Stick to "Good Enough" text extraction for v1.
2.  **Encoding Hell**: EPUBs usually assume UTF-8, but be careful with strange characters.
3.  **Memory Usage**: Loading a massive PDF or EPUB into memory might be heavy. Keep an eye on `read()` operations.

---

## 🎯 Success Criteria for Week 2

-   [ ] `PDFParser` can read a standard ebook PDF.
-   [ ] `MarkdownParser` correctly identifies chapters from headers.
-   [ ] `EpubParser` extracts content + metadata without HTML tags.
-   [ ] `get_parser(path)` correctly identifies and initializes all 3 new types.
-   [ ] Run `python -m app.app mybook.pdf` and see the text summary.
