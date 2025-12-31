"""Metadata model definition."""

from typing import Optional

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

class Metadata(Base):
    """
    Model for storing additional book metadata.
    """
    __tablename__ = "metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), unique=True, index=True)
    
    # Book Metadata
    publisher: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    published_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    isbn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="metadata_info")

    def __repr__(self) -> str:
        return f"<Metadata(doc={self.document_id}, isbn='{self.isbn}')>"
