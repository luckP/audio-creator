"""Tests for database models."""

import pytest
from sqlalchemy import select
from datetime import datetime

from app.models import Document, Chapter, Metadata, AudioJob, ProcessingStatus, get_session_factory, init_database, Base, get_engine
from app.utils.config import get_config

# Use the same setup as other tests, but specifically for model interactions
@pytest.fixture
def db_session():
    """Create a temporary database session for testing."""
    # Use in-memory SQLite for speed and isolation
    config = get_config()
    config.database.path = ":memory:"
    
    init_database()
    
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=get_engine())

def test_create_document_with_relationships(db_session):
    """Test creating a document with chapters and metadata."""
    
    # 1. Create Document
    doc = Document(
        title="Test Book",
        author="Test Author",
        source_file="/tmp/test.pdf",
        format="pdf",
        status=ProcessingStatus.PENDING
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    
    assert doc.id is not None
    assert doc.title == "Test Book"
    assert doc.status == "pending"
    
    # 2. Add Chapter
    chapter = Chapter(
        document_id=doc.id,
        number=1,
        title="Chapter 1",
        content="This is the content of chapter 1."
    )
    db_session.add(chapter)
    db_session.commit()
    
    # 3. Add Metadata
    meta = Metadata(
        document_id=doc.id,
        publisher="Test Publisher",
        isbn="123-456-789",
        language="en"
    )
    db_session.add(meta)
    db_session.commit()
    
    # 4. Add Audio Job
    job = AudioJob(
        document_id=doc.id,
        voice_id="Alex",
        status="pending"
    )
    db_session.add(job)
    db_session.commit()
    
    # 5. Verify Relationships via Query
    # Clear session to ensure we are pulling from DB, not memory cache
    db_session.expire_all()
    
    # Query Document with relationships
    stmt = select(Document).where(Document.id == doc.id)
    retrieved_doc = db_session.scalars(stmt).one()
    
    # Check Document fields
    assert retrieved_doc.title == "Test Book"
    
    # Check Chapter relationship
    assert len(retrieved_doc.chapters) == 1
    assert retrieved_doc.chapters[0].title == "Chapter 1"
    assert retrieved_doc.chapters[0].document_id == retrieved_doc.id
    
    # Check Metadata relationship
    assert retrieved_doc.metadata_info is not None
    assert retrieved_doc.metadata_info.publisher == "Test Publisher"
    
    # Check AudioJob relationship
    assert len(retrieved_doc.audio_jobs) == 1
    assert retrieved_doc.audio_jobs[0].voice_id == "Alex"

def test_cascade_delete(db_session):
    """Test that deleting a document also deletes its chapters and metadata."""
    
    # Create full structure
    doc = Document(title="Delete Me", source_file="x", format="txt")
    db_session.add(doc)
    db_session.commit()
    
    chapter = Chapter(document_id=doc.id, number=1, title="Ch1", content="...")
    meta = Metadata(document_id=doc.id, isbn="111")
    db_session.add_all([chapter, meta])
    db_session.commit()
    
    doc_id = doc.id
    
    # Delete Document
    db_session.delete(doc)
    db_session.commit()
    
    # Verify deletions
    assert db_session.get(Document, doc_id) is None
    
    # Check if children are gone
    # Note: query by filter because direct get might fail if ID logic differs
    orphaned_chapters = db_session.scalars(
        select(Chapter).where(Chapter.document_id == doc_id)
    ).all()
    assert len(orphaned_chapters) == 0
    
    orphaned_meta = db_session.scalars(
        select(Metadata).where(Metadata.document_id == doc_id)
    ).all()
    assert len(orphaned_meta) == 0
