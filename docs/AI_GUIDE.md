# AI Agent Development Guide

This document provides comprehensive information for AI agents working on the Intelligent Audiobook Creator project.

## 🎯 Project Overview

**Purpose**: Convert documents (PDF, Markdown, EPUB, TXT) into high-quality audiobooks with intelligent processing.

**Key Objectives**:
1. Parse multiple document formats accurately
2. Intelligently detect document structure (chapters, sections, titles)
3. Clean and normalize text for audio generation
4. Generate high-quality audio with proper pacing
5. Create structured audiobook files with metadata

## 🏗️ Architecture

### Core Components

#### 1. Parsers (`app/parsers/`)
**Purpose**: Extract text from various document formats

- `base_parser.py`: Abstract base class for all parsers
- `pdf_parser.py`: PDF document parsing using pdfplumber
- `markdown_parser.py`: Markdown parsing with structure preservation
- `epub_parser.py`: EPUB ebook parsing
- `text_parser.py`: Plain text file parsing

**Key Interfaces**:
```python
class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> Document:
        """Parse document and return structured Document object"""
        pass
```

#### 2. Processors (`app/processors/`)
**Purpose**: Clean, normalize, and structure extracted text

- `text_cleaner.py`: Remove artifacts (page numbers, headers, footers)
- `structure_detector.py`: Detect chapters, sections, hierarchy
- `metadata_extractor.py`: Extract book metadata
- `content_normalizer.py`: Normalize whitespace, fix hyphenation

**Processing Pipeline**:
```
Raw Text → Clean → Detect Structure → Extract Metadata → Normalized Document
```

#### 3. Models (`app/models/`)
**Purpose**: Data models and database schema

- `document.py`: Document model with SQLAlchemy ORM
- `chapter.py`: Chapter model
- `section.py`: Section model
- `metadata.py`: Metadata model
- `database.py`: Database connection and session management

**Database**: SQLite with SQLAlchemy ORM

#### 4. Audio (`app/audio/`)
**Purpose**: Generate and process audio files

- `generator.py`: Text-to-speech generation
- `combiner.py`: Combine multiple audio files
- `converter.py`: Convert between audio formats
- `tagger.py`: Add ID3 tags and chapter markers

**Audio Pipeline**:
```
Text → TTS Generation → Combine Chapters → Convert Format → Add Metadata
```

#### 5. Utils (`app/utils/`)
**Purpose**: Shared utilities and helpers

- `config.py`: Configuration management
- `logger.py`: Logging setup
- `validators.py`: Input validation
- `init_db.py`: Database initialization

## 📊 Data Flow

```
Input File (PDF/MD/EPUB/TXT)
    ↓
Parser (extract text)
    ↓
Processor (clean & structure)
    ↓
Database (store metadata)
    ↓
Audio Generator (create audio)
    ↓
Combiner (merge chapters)
    ↓
Converter (final format)
    ↓
Output Audiobook (MP3/M4B)
```

## 🗄️ Database Schema

### Tables

#### `documents`
- `id`: Primary key
- `title`: Document title
- `author`: Author name
- `source_file`: Original file path
- `source_format`: File format (pdf, md, epub, txt)
- `created_at`: Timestamp
- `updated_at`: Timestamp

#### `chapters`
- `id`: Primary key
- `document_id`: Foreign key to documents
- `number`: Chapter number
- `title`: Chapter title
- `content`: Chapter text content
- `word_count`: Word count
- `audio_file`: Path to generated audio
- `duration`: Audio duration in seconds

#### `metadata`
- `id`: Primary key
- `document_id`: Foreign key to documents
- `publisher`: Publisher name
- `year`: Publication year
- `isbn`: ISBN number
- `language`: Language code

## 🔧 Configuration

### Config Files (`config/`)

#### `default_config.yaml`
```yaml
audio:
  voice: "Alex"
  speed: 1.0
  format: "mp3"
  quality: "high"
  
processing:
  detect_chapters: true
  clean_text: true
  remove_page_numbers: true
  
output:
  separate_chapters: false
  add_metadata: true
  cleanup_intermediate: true
```

## 🧪 Testing Strategy

### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Mock external dependencies
- Fast execution

### Integration Tests (`tests/integration/`)
- Test component interactions
- Use test database
- Test full workflows

### Test Coverage Target
- Minimum: 80%
- Goal: 90%+

## 📝 Code Standards

### Style Guide
- **Formatter**: Black (line length: 100)
- **Linter**: Pylint
- **Type Checker**: MyPy
- **Import Sorter**: isort

### Naming Conventions
- **Classes**: PascalCase (`DocumentParser`)
- **Functions**: snake_case (`parse_document`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- **Private**: Leading underscore (`_internal_method`)

### Documentation
- **Docstrings**: Google style
- **Type Hints**: Required for all functions
- **Comments**: Explain "why", not "what"

## 🚀 Development Workflow

### Adding a New Feature

1. **Create Branch**: `feature/feature-name`
2. **Write Tests**: Test-driven development
3. **Implement**: Follow code standards
4. **Document**: Update relevant docs
5. **Test**: Run full test suite
6. **Commit**: Clear, descriptive messages
7. **PR**: Submit for review

### Adding a New Parser

1. Create parser class inheriting from `BaseParser`
2. Implement `parse()` method
3. Add tests in `tests/unit/test_parsers.py`
4. Update documentation
5. Register parser in `app/parsers/__init__.py`

### Adding a New Processor

1. Create processor class in `app/processors/`
2. Define clear input/output interfaces
3. Add comprehensive tests
4. Document processing logic
5. Integrate into processing pipeline

## 🐛 Common Issues & Solutions

### Issue: PDF Text Extraction Garbled
**Solution**: Use `pdfplumber` instead of `PyPDF2` for better OCR

### Issue: Chapter Detection Fails
**Solution**: Check regex patterns in `structure_detector.py`, may need tuning

### Issue: Audio Generation Timeout
**Solution**: Increase timeout in config, check text chunk size

## 📚 Key Dependencies

### Document Parsing
- `pdfplumber`: Best for PDF text extraction
- `ebooklib`: EPUB parsing
- `markdown`: Markdown to HTML conversion

### Audio Processing
- `pydub`: Audio manipulation
- `mutagen`: Metadata tagging
- System: `ffmpeg`, `sox`

### Database
- `sqlalchemy`: ORM
- `alembic`: Migrations

## 🎯 Current Implementation Status

### ✅ Completed
- Project structure
- Documentation framework
- Dependency management

### 🚧 In Progress
- Base models and database schema
- Parser implementations
- Audio generation pipeline

### 📋 Planned
- Chapter detection algorithms
- Metadata extraction
- M4B format support
- Web interface

## 💡 Best Practices for AI Agents

1. **Always check existing code** before implementing new features
2. **Follow the established patterns** in the codebase
3. **Write tests first** (TDD approach)
4. **Update documentation** with code changes
5. **Use type hints** for better code clarity
6. **Handle errors gracefully** with proper exception handling
7. **Log important operations** for debugging
8. **Keep functions focused** (single responsibility)
9. **Avoid hardcoding** - use configuration
10. **Think about edge cases** in implementation

## 🔍 Code Review Checklist

- [ ] Type hints present and correct
- [ ] Docstrings complete (Google style)
- [ ] Tests written and passing
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Logging added for key operations
- [ ] Documentation updated
- [ ] Code formatted (black, isort)
- [ ] Linting passes (pylint)
- [ ] Type checking passes (mypy)

## 📞 Getting Help

When stuck:
1. Check this guide
2. Review existing similar code
3. Check test files for usage examples
4. Review architecture documentation
5. Ask for clarification with specific context

---

**Remember**: Clean, well-documented, tested code is more valuable than clever code.
