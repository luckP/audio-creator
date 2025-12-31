"""Chapter model definition."""

from typing import Optional

from sqlalchemy import String, Text, Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

class Chapter(Base):
    """
    Chapter model representing a section of a document.
    Stores extracted text and paths to generated audio.
    """
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    
    # Ordering and Structure
    number: Mapped[int] = mapped_column(Integer)  # Sequential order
    title: Mapped[str] = mapped_column(String(255))
    
    # Content
    content: Mapped[str] = mapped_column(Text)  # The actual text content
    
    # Audio Generation Results
    audio_file: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chapters")

    def __repr__(self) -> str:
        return f"<Chapter(doc={self.document_id}, number={self.number}, title='{self.title}')>"
