# Intelligent Audiobook Creator

A professional, modular system for converting documents (PDF, Markdown, EPUB, TXT) into high-quality audiobooks with intelligent text processing, chapter detection, and metadata extraction.

## 🎯 Features

- **Multi-Format Support**: PDF, Markdown, EPUB, and plain text
- **Intelligent Processing**:
  - Automatic chapter detection
  - Smart text cleanup (removes page numbers, headers, footers)
  - Structure recognition (titles, subtitles, sections)
  - Metadata extraction
- **High-Quality Audio**:
  - Per-chapter audio generation
  - Multiple output formats (MP3, M4B)
  - Embedded chapter markers
  - ID3 metadata tagging
- **Database-Backed**: SQLite for tracking conversions and metadata
- **Modern Architecture**: Clean, testable, extensible codebase

## 📋 Requirements

- Python 3.9+
- macOS (for `say` command) or alternative TTS engine
- FFmpeg (for audio conversion)
- SoX (for audio processing)

### Installation

```bash
# Install system dependencies (macOS)
brew install ffmpeg sox

# Clone repository
git clone <repository-url>
cd audio-creator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate  # On Windows

# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python -m app.utils.init_db
```

## 🚀 Quick Start

```bash
# Basic usage - convert a PDF to audiobook
python -m app.app book.pdf

# With custom output directory
python -m app.app book.pdf --output-dir ./audiobooks/my-book

# Generate M4B with chapter markers
python -m app.app book.epub --format m4b --detect-chapters

# Advanced options
python -m app.app book.md \
  --voice Alex \
  --speed 1.2 \
  --chapters-separate \
  --clean-text
```

## 📖 Usage Examples

### Convert PDF to Audiobook
```bash
python -m app.app document.pdf --output-dir ./output
```

### Convert Markdown with Chapter Detection
```bash
python -m app.app book.md --detect-chapters --format m4b
```

### Custom Voice Settings
```bash
python -m app.app book.txt --voice Samantha --speed 1.1
```

## 🏗️ Project Structure

```
audio-creator/
├── app/                      # Main application code
│   ├── parsers/             # Document parsers (PDF, MD, EPUB)
│   ├── processors/          # Text processing & cleanup
│   ├── models/              # Data models & database
│   ├── audio/               # Audio generation & processing
│   ├── utils/               # Utilities & helpers
│   └── app.py               # CLI entry point
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── docs/                     # Documentation
├── config/                   # Configuration files
├── examples/                 # Example documents
└── legacy/                   # Legacy code (archived)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_parsers.py
```

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [AI Agent Guide](docs/AI_GUIDE.md)

## 🛠️ Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
pylint app/

# Format code
black app/ tests/

# Type checking
mypy app/
```

## 🗄️ Database Schema

The application uses SQLite to track:
- Document conversions
- Chapter metadata
- Audio generation history
- Configuration settings

See [Database Schema](docs/DATABASE.md) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with modern Python best practices
- Inspired by the need for accessible audiobook creation
- Community-driven development

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Status**: 🚧 Active Development - v0.1.0-alpha
