"""
AnnotationTranslation model for storing multiple translations of the same annotation.
Each annotation can have up to 3 translations from different users.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AnnotationTranslation(Base):
    """
    Stores translations for annotations.
    Each row represents one user's translation of one annotation.
    An annotation can have multiple translations (up to 3 from different users).
    """
    __tablename__ = "annotation_translations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign keys
    annotation_id: Mapped[int] = mapped_column(ForeignKey("annotations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Translation fields
    question_gn: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Translated question in Guaraní
    answer_gn: Mapped[Optional[str]] = mapped_column(Text, nullable=True)    # Translated answer in Guaraní
    validated: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    annotation = relationship("Annotation", back_populates="translations")
    user = relationship("User", back_populates="annotation_translations")
    validations = relationship("AnnotationValidation", back_populates="translation", cascade="all, delete-orphan")
    suggestions = relationship("AnnotationSuggestion", back_populates="translation", cascade="all, delete-orphan")
