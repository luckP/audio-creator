# Week 1 Action Plan - Getting Started

**Goal**: Set up foundation with database models and base parser interface

---

## 🎯 This Week's Objectives

1. ✅ Set up database schema and models
2. ✅ Create base parser interface
3. ✅ Implement text parser (simplest case)
4. ✅ Write initial tests
5. ✅ Verify configuration and logging systems

---

## 📋 Day-by-Day Breakdown

### Day 1: Database Foundation
**Tasks**:
1. Install database dependencies
   ```bash
   pip install sqlalchemy alembic
   pip freeze > requirements.txt
   ```

2. Create database engine and session management
   - File: `app/models/database.py`
   - Set up SQLAlchemy engine
   - Create session factory
   - Add connection pooling

3. Create Document model
   - File: `app/models/document.py`
   - Fields: id, title, author, source_file, format, created_at, etc.
   - Add relationships

**Deliverable**: Working database connection and Document model

---

### Day 2: Complete Database Models
**Tasks**:
1. Create Chapter model
   - File: `app/models/chapter.py`
   - Fields: id, document_id, number, title, content, audio_file, etc.
   - Relationship to Document

2. Create AudioJob model
   - File: `app/models/audio_job.py`
   - Track processing status, progress, errors

3. Create Metadata model
   - File: `app/models/metadata.py`
   - Publisher, ISBN, language, etc.

4. Set up Alembic migrations
   ```bash
   alembic init alembic
   alembic revision --autogenerate -m "Initial schema"
   ```

**Deliverable**: Complete database schema with migrations

---

### Day 3: Database Initialization & Tests
**Tasks**:
1. Create database initialization script
   - File: `app/utils/init_db.py`
   - Create tables
   - Add sample data for testing

2. Write database tests
   - File: `tests/unit/test_models.py`
   - Test model creation
   - Test relationships
   - Test queries

3. Update `__init__.py` files for proper imports

**Deliverable**: Tested, working database layer

---

### Day 4: Base Parser Interface
**Tasks**:
1. Create abstract BaseParser class
   - File: `app/parsers/base_parser.py`
   - Define `parse()` abstract method
   - Define Document data structure
   - Add common utilities

2. Create parser registry/factory
   - File: `app/parsers/__init__.py`
   - Auto-register parsers
   - Factory method to get parser by file extension

3. Write base parser tests
   - File: `tests/unit/test_base_parser.py`

**Deliverable**: Parser framework ready for implementations

---

### Day 5: Text Parser Implementation
**Tasks**:
1. Implement TextParser
   - File: `app/parsers/text_parser.py`
   - Inherit from BaseParser
   - Read text files
   - Create Document object
   - Handle encoding issues

2. Refactor legacy `read_file()` logic
   - Improve error handling
   - Add encoding detection

3. Write comprehensive tests
   - File: `tests/unit/test_text_parser.py`
   - Test various text files
   - Test edge cases (empty, large files, etc.)

**Deliverable**: Working text parser with tests

---

### Weekend: Integration & Documentation
**Tasks**:
1. Write integration test
   - Parse text file → Save to database → Verify

2. Update documentation
   - Document database schema
   - Document parser interface
   - Add code examples

3. Code review and cleanup
   - Run linting: `pylint app/`
   - Format code: `black app/ tests/`
   - Check types: `mypy app/`

4. Update DEVELOPMENT_PLAN.md with progress

**Deliverable**: Clean, tested, documented foundation

---

## 🏗️ File Structure After Week 1

```
audio-creator/
├── app/
│   ├── models/
│   │   ├── __init__.py          ✅ NEW
│   │   ├── database.py          ✅ NEW
│   │   ├── document.py          ✅ NEW
│   │   ├── chapter.py           ✅ NEW
│   │   ├── audio_job.py         ✅ NEW
│   │   └── metadata.py          ✅ NEW
│   ├── parsers/
│   │   ├── __init__.py          ✅ NEW
│   │   ├── base_parser.py       ✅ NEW
│   │   └── text_parser.py       ✅ NEW
│   └── utils/
│       ├── init_db.py           ✅ NEW
│       ├── config.py            ✅ EXISTS
│       └── logger.py            ✅ EXISTS
├── tests/
│   └── unit/
│       ├── test_models.py       ✅ NEW
│       ├── test_base_parser.py  ✅ NEW
│       └── test_text_parser.py  ✅ NEW
├── alembic/                     ✅ NEW
│   └── versions/
└── audiobooks.db                ✅ NEW (created by init_db)
```

---

## 📚 Key Concepts to Understand

### 1. SQLAlchemy ORM
- Declarative base classes
- Relationships (one-to-many, many-to-one)
- Sessions and transactions
- Queries and filters

### 2. Abstract Base Classes (ABC)
- Define interfaces
- Enforce implementation of methods
- Enable polymorphism

### 3. Factory Pattern
- Create objects without specifying exact class
- Parser factory selects parser based on file type

---

## 🧪 Testing Strategy

### Unit Tests
- Test each model independently
- Mock database for parser tests
- Test edge cases and error conditions

### Integration Tests
- Test full flow: parse → save → retrieve
- Use test database (separate from production)

### Coverage Goal
- Aim for 80%+ coverage from day 1
- Run: `pytest --cov=app --cov-report=html`

---

## 🔧 Development Commands

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run linting
pylint app/

# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/

# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Initialize database
python -m app.utils.init_db
```

---

## ⚠️ Common Pitfalls to Avoid

1. **Don't skip tests** - Write tests as you code
2. **Don't hardcode paths** - Use Path objects and config
3. **Don't ignore type hints** - They catch bugs early
4. **Don't commit without linting** - Keep code clean
5. **Don't forget docstrings** - Document as you go

---

## 🎯 Success Criteria for Week 1

By end of week, you should have:
- [ ] Working database with all models
- [ ] Alembic migrations set up
- [ ] Base parser interface defined
- [ ] Text parser implemented and tested
- [ ] 80%+ test coverage for new code
- [ ] All code linted and formatted
- [ ] Documentation updated

---

## 🚀 Getting Started Right Now

### Step 1: Install Dependencies
```bash
cd /Users/lucparada/Projects/audio-creator
source .venv/bin/activate
pip install sqlalchemy alembic
pip freeze > requirements.txt
```

### Step 2: Create First File
Start with `app/models/database.py`:

```python
"""Database engine and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from typing import Generator

from ..utils.config import get_config

# Base class for all models
Base = declarative_base()

# Database engine (singleton)
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        config = get_config()
        db_path = Path(config.database.path)
        db_url = f"sqlite:///{db_path}"
        _engine = create_engine(
            db_url,
            echo=config.database.echo,
            connect_args={"check_same_thread": False}
        )
    return _engine


def get_session_factory():
    """Get or create session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        Session: SQLAlchemy session
        
    Example:
        with get_db() as db:
            documents = db.query(Document).all()
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database - create all tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
```

### Step 3: Run Tests
```bash
pytest tests/unit/test_models.py -v
```

---

**You're ready to start! Begin with database.py and work through the days sequentially. Good luck! 🚀**
