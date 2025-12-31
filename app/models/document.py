"""Document model definition."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, DateTime, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

class ProcessingStatus(str, SqlEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(Base):
    """
    Document model representing a source file (PDF, EPUB, etc.)
    being converted to an audiobook.
    """
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_file: Mapped[str] = mapped_column(String(1024))  # Path to source file
    format: Mapped[str] = mapped_column(String(10))  # pdf, epub, txt, md
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    # Note: using string reference "Chapter" to avoid circular imports
    chapters: Mapped[List["Chapter"]] = relationship(
        "Chapter", back_populates="document", cascade="all, delete-orphan"
    )
    
    # Metadata will be one-to-one
    metadata_info: Mapped[Optional["Metadata"]] = relationship(
        "Metadata", back_populates="document", uselist=False, cascade="all, delete-orphan"
    )
    
    # Job history
    audio_jobs: Mapped[List["AudioJob"]] = relationship(
        "AudioJob", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title='{self.title}', status='{self.status}')>"
