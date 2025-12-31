"""Audio generation job model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

class AudioJob(Base):
    """
    Model getting the status and progress of an audio generation task.
    Allows for background processing and resuming.
    """
    __tablename__ = "audio_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    
    # Configuration Snapshot (stores how this job was configured)
    voice_id: Mapped[str] = mapped_column(String(50))
    speed: Mapped[float] = mapped_column(default=1.0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    current_chapter: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="audio_jobs")

    def __repr__(self) -> str:
        return f"<AudioJob(id={self.id}, doc={self.document_id}, status='{self.status}')>"
