# Audiobook Creator - Development Plan

**Project**: Intelligent Audiobook Creator  
**Version**: 0.1.0-alpha  
**Last Updated**: 2025-12-30  
**Status**: 🚧 Active Development

---

## 📋 Executive Summary

This document outlines the development plan to transform the existing legacy audio creator script into a professional, modular audiobook creation system. The goal is to build a robust application that converts documents (PDF, Markdown, EPUB, TXT) into high-quality audiobooks with intelligent processing, chapter detection, and metadata management.

### Current State
- ✅ **Configuration System**: Pydantic-based config with YAML support
- ✅ **Logging System**: Structured logging with file/console output
- ✅ **Legacy Script**: Working text-to-audio converter (in `legacy/main.py`)
- ⚠️ **Core Modules**: Empty directories (parsers, processors, models, audio)

### Target State
A complete, production-ready audiobook creation system with:
- Multi-format document parsing
- Intelligent text processing and chapter detection
- Database-backed metadata management
- High-quality audio generation with chapter markers
- CLI and potential web interface

---

## 🎯 Development Phases

## Phase 1: Foundation & Core Models (Week 1)
**Goal**: Establish database schema and core data models

### Tasks

#### 1.1 Database Setup
- [ ] Create SQLAlchemy models for:
  - `Document` (source files, metadata)
  - `Chapter` (chapter content, audio files)
  - `AudioJob` (processing queue, status tracking)
  - `Metadata` (book metadata, tags)
- [ ] Set up Alembic for database migrations
- [ ] Create database initialization script
- [ ] Add database session management utilities

**Files to Create**:
- `app/models/database.py` - Database engine and session management
- `app/models/document.py` - Document model
- `app/models/chapter.py` - Chapter model
- `app/models/audio_job.py` - Audio job tracking
- `app/models/metadata.py` - Metadata model
- `app/utils/init_db.py` - Database initialization
- `alembic/` - Migration framework setup

**Estimated Time**: 2-3 days

---

#### 1.2 Base Parser Interface
- [ ] Create abstract `BaseParser` class
- [ ] Define `Document` data structure
- [ ] Implement basic text parser (simplest case)
- [ ] Add parser factory/registry pattern
- [ ] Write unit tests for base parser

**Files to Create**:
- `app/parsers/base_parser.py` - Abstract base class
- `app/parsers/text_parser.py` - Plain text implementation
- `app/parsers/__init__.py` - Parser registry
- `tests/unit/test_base_parser.py` - Tests

**Estimated Time**: 1-2 days

---

## Phase 2: Document Parsers (Week 2)
**Goal**: Implement parsers for all supported formats

### Tasks

#### 2.1 PDF Parser
- [ ] Implement PDF text extraction using `pdfplumber`
- [ ] Handle multi-column layouts
- [ ] Extract basic metadata (title, author)
- [ ] Preserve structure (headings, paragraphs)
- [ ] Add error handling for corrupted PDFs
- [ ] Write comprehensive tests

**Files to Create**:
- `app/parsers/pdf_parser.py`
- `tests/unit/test_pdf_parser.py`
- `tests/fixtures/sample.pdf` - Test file

**Estimated Time**: 2-3 days

---

#### 2.2 Markdown Parser
- [ ] Implement Markdown parsing with structure preservation
- [ ] Extract headings hierarchy (H1, H2, H3)
- [ ] Handle code blocks, lists, formatting
- [ ] Extract front matter metadata (if present)
- [ ] Write tests with various Markdown features

**Files to Create**:
- `app/parsers/markdown_parser.py`
- `tests/unit/test_markdown_parser.py`
- `tests/fixtures/sample.md` - Test file

**Estimated Time**: 1-2 days

---

#### 2.3 EPUB Parser
- [ ] Implement EPUB parsing using `ebooklib`
- [ ] Extract chapters from EPUB structure
- [ ] Parse embedded metadata
- [ ] Handle images and special content
- [ ] Write tests with real EPUB files

**Files to Create**:
- `app/parsers/epub_parser.py`
- `tests/unit/test_epub_parser.py`
- `tests/fixtures/sample.epub` - Test file

**Estimated Time**: 2-3 days

---

## Phase 3: Text Processing (Week 3)
**Goal**: Implement intelligent text cleaning and structure detection

### Tasks

#### 3.1 Text Cleaner
- [ ] Remove page numbers (various formats)
- [ ] Remove headers and footers
- [ ] Fix hyphenation at line breaks
- [ ] Normalize whitespace
- [ ] Remove special characters/artifacts
- [ ] Make configurable via settings
- [ ] Write extensive tests

**Files to Create**:
- `app/processors/text_cleaner.py`
- `tests/unit/test_text_cleaner.py`

**Estimated Time**: 2 days

---

#### 3.2 Structure Detector
- [ ] Implement chapter detection using regex patterns
- [ ] Detect section hierarchy
- [ ] Identify titles and subtitles
- [ ] Handle multiple chapter formats
- [ ] Make patterns configurable
- [ ] Write tests with various formats

**Files to Create**:
- `app/processors/structure_detector.py`
- `tests/unit/test_structure_detector.py`

**Estimated Time**: 2-3 days

---

#### 3.3 Metadata Extractor
- [ ] Extract document metadata
- [ ] Parse author, title, publisher
- [ ] Extract ISBN, publication date
- [ ] Handle multiple metadata sources
- [ ] Write tests

**Files to Create**:
- `app/processors/metadata_extractor.py`
- `tests/unit/test_metadata_extractor.py`

**Estimated Time**: 1-2 days

---

## Phase 4: Audio Generation (Week 4)
**Goal**: Implement audio generation pipeline

### Tasks

#### 4.1 Audio Generator (Refactor from Legacy)
- [ ] Refactor legacy `create_aiff_files()` into class
- [ ] Add support for multiple TTS engines
- [ ] Implement voice selection
- [ ] Add speed/quality controls
- [ ] Implement retry logic with exponential backoff
- [ ] Add progress tracking
- [ ] Write tests (with mocked TTS)

**Files to Create**:
- `app/audio/generator.py`
- `app/audio/tts_engines/` - TTS engine abstractions
- `tests/unit/test_audio_generator.py`

**Estimated Time**: 2-3 days

---

#### 4.2 Audio Combiner (Refactor from Legacy)
- [ ] Refactor legacy `combine_aiff_files()` into class
- [ ] Support multiple audio formats
- [ ] Add chapter markers
- [ ] Implement crossfade between chapters
- [ ] Add silence detection/removal
- [ ] Write tests

**Files to Create**:
- `app/audio/combiner.py`
- `tests/unit/test_audio_combiner.py`

**Estimated Time**: 2 days

---

#### 4.3 Audio Converter (Refactor from Legacy)
- [ ] Refactor legacy `convert_to_mp3()` into class
- [ ] Support MP3, M4B, AAC formats
- [ ] Implement quality/bitrate controls
- [ ] Add metadata embedding
- [ ] Add cover art support
- [ ] Write tests

**Files to Create**:
- `app/audio/converter.py`
- `tests/unit/test_audio_converter.py`

**Estimated Time**: 2 days

---

#### 4.4 Metadata Tagger
- [ ] Implement ID3 tag writing
- [ ] Add chapter markers (M4B)
- [ ] Embed cover art
- [ ] Add book metadata (author, title, etc.)
- [ ] Write tests

**Files to Create**:
- `app/audio/tagger.py`
- `tests/unit/test_tagger.py`

**Estimated Time**: 1-2 days

---

## Phase 5: CLI & Orchestration (Week 5)
**Goal**: Build command-line interface and orchestrate all components

### Tasks

#### 5.1 Main Application Logic
- [ ] Create main application class
- [ ] Implement processing pipeline orchestration
- [ ] Add job queue management
- [ ] Implement progress tracking
- [ ] Add error recovery
- [ ] Write integration tests

**Files to Create**:
- `app/main.py` - Main application
- `app/orchestrator.py` - Pipeline orchestration
- `tests/integration/test_full_pipeline.py`

**Estimated Time**: 2-3 days

---

#### 5.2 CLI Interface
- [ ] Implement argument parsing (Click or argparse)
- [ ] Add command: `create` - Create audiobook
- [ ] Add command: `list` - List conversions
- [ ] Add command: `status` - Check job status
- [ ] Add command: `config` - Manage configuration
- [ ] Add rich progress bars and output
- [ ] Write CLI tests

**Files to Create**:
- `app/cli.py` - CLI interface
- `tests/integration/test_cli.py`

**Estimated Time**: 2 days

---

#### 5.3 Error Handling & Validation
- [ ] Create custom exception hierarchy
- [ ] Add input validation
- [ ] Implement graceful error recovery
- [ ] Add detailed error messages
- [ ] Write tests for error cases

**Files to Create**:
- `app/exceptions.py` - Custom exceptions
- `app/utils/validators.py` - Input validation
- `tests/unit/test_validators.py`

**Estimated Time**: 1-2 days

---

## Phase 6: Testing & Documentation (Week 6)
**Goal**: Achieve high test coverage and complete documentation

### Tasks

#### 6.1 Testing
- [ ] Achieve 80%+ unit test coverage
- [ ] Write integration tests for full pipeline
- [ ] Add performance tests
- [ ] Create test fixtures for all formats
- [ ] Set up CI/CD pipeline (GitHub Actions)

**Estimated Time**: 2-3 days

---

#### 6.2 Documentation
- [ ] Complete API documentation
- [ ] Write user guide
- [ ] Create examples and tutorials
- [ ] Document configuration options
- [ ] Add troubleshooting guide

**Files to Update/Create**:
- `docs/API.md`
- `docs/USER_GUIDE.md`
- `docs/EXAMPLES.md`
- `docs/TROUBLESHOOTING.md`

**Estimated Time**: 2 days

---

#### 6.3 Performance Optimization
- [ ] Profile audio generation
- [ ] Optimize text processing
- [ ] Implement parallel processing
- [ ] Add caching where appropriate
- [ ] Benchmark and document performance

**Estimated Time**: 1-2 days

---

## Phase 7: Advanced Features (Week 7+)
**Goal**: Add advanced features for production use

### Tasks

#### 7.1 M4B Support
- [ ] Implement M4B container format
- [ ] Add embedded chapter markers
- [ ] Support chapter images
- [ ] Write tests

**Estimated Time**: 2-3 days

---

#### 7.2 Web Interface (Optional)
- [ ] Design REST API
- [ ] Create simple web UI
- [ ] Add job queue visualization
- [ ] Implement file upload
- [ ] Add authentication

**Estimated Time**: 1-2 weeks

---

#### 7.3 Cloud TTS Integration (Optional)
- [ ] Add Google Cloud TTS support
- [ ] Add AWS Polly support
- [ ] Add Azure TTS support
- [ ] Make TTS engine pluggable

**Estimated Time**: 1 week

---

## 📦 Dependencies to Add

### Core Dependencies
```
# Already in requirements.txt
pydantic>=2.0.0
pyyaml>=6.0.0

# To be added
sqlalchemy>=2.0.0
alembic>=1.12.0
pdfplumber>=0.10.0
ebooklib>=0.18
markdown>=3.5.0
pydub>=0.25.0
mutagen>=1.47.0
click>=8.1.0
rich>=13.0.0  # For beautiful CLI output
```

### Development Dependencies
```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
black>=23.0.0
pylint>=3.0.0
mypy>=1.7.0
isort>=5.12.0
```

---

## 🎯 Success Criteria

### Phase 1-3 (Weeks 1-3)
- [ ] All parsers working with test files
- [ ] Text processing pipeline functional
- [ ] Database schema complete and tested
- [ ] 70%+ test coverage

### Phase 4-5 (Weeks 4-5)
- [ ] Audio generation working end-to-end
- [ ] CLI functional for basic use cases
- [ ] Can convert a simple text file to MP3
- [ ] 80%+ test coverage

### Phase 6-7 (Weeks 6-7)
- [ ] Production-ready release
- [ ] Complete documentation
- [ ] All formats supported
- [ ] 85%+ test coverage
- [ ] Performance benchmarks documented

---

## 🚀 Quick Start for Development

### Immediate Next Steps (This Week)

1. **Set up development environment**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Create database models** (Phase 1.1)
   - Start with `app/models/database.py`
   - Then `app/models/document.py`

3. **Implement base parser** (Phase 1.2)
   - Create `app/parsers/base_parser.py`
   - Implement `app/parsers/text_parser.py`

4. **Write tests as you go**
   - Test-driven development approach
   - Aim for 80%+ coverage from the start

---

## 📊 Project Metrics

### Estimated Timeline
- **Minimum Viable Product (MVP)**: 4-5 weeks
- **Production Ready**: 6-7 weeks
- **With Advanced Features**: 8-10 weeks

### Estimated Effort
- **Core Development**: ~120-150 hours
- **Testing**: ~30-40 hours
- **Documentation**: ~20-30 hours
- **Total**: ~170-220 hours

---

## 🔄 Migration Strategy from Legacy

The legacy script (`legacy/main.py`) contains working code that we'll refactor:

1. **`create_aiff_files()`** → `app/audio/generator.py`
2. **`combine_aiff_files()`** → `app/audio/combiner.py`
3. **`convert_to_mp3()`** → `app/audio/converter.py`
4. **`split_file()`** → `app/processors/text_chunker.py`
5. **`read_file()`** → `app/parsers/text_parser.py`

**Strategy**: 
- Keep legacy code working during development
- Refactor incrementally with tests
- Remove legacy code only when new system is complete

---

## 🎨 Architecture Principles

1. **Modularity**: Each component is independent and testable
2. **Configurability**: All behavior controlled via config files
3. **Extensibility**: Easy to add new parsers, TTS engines, formats
4. **Robustness**: Comprehensive error handling and recovery
5. **Performance**: Parallel processing where possible
6. **Maintainability**: Clean code, well-documented, tested

---

## 📝 Notes

- This is a living document - update as priorities change
- Focus on MVP first, then iterate
- Test-driven development is crucial
- Keep the legacy script working until new system is complete
- Document decisions and trade-offs as you go

---

## ✅ Review Checklist

Before starting development, ensure:
- [ ] All dependencies are installed
- [ ] Development environment is set up
- [ ] You understand the architecture (see `docs/AI_GUIDE.md`)
- [ ] You've reviewed the legacy code
- [ ] You have test files for each format
- [ ] Database design is clear

---

**Ready to start? Begin with Phase 1.1: Database Setup! 🚀**
