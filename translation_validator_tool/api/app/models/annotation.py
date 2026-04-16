"""
Annotation model for storing question-answer pairs.
Translations are now stored separately in AnnotationTranslation table to support
multiple translations per annotation (up to 3 from different users).
Assignments are now stored in AnnotationAssignment table to support many-to-many
relationship between annotations and translators.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Annotation(Base):
    __tablename__ = "annotations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Question fields (original, in Spanish)
    question_es: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Original question in Spanish
    
    # Answer fields (original, in Spanish)
    answer_es: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Original answer in Spanish
    
    # Metadata fields
    answer_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Numeric answer (e.g., 18)
    equation_solution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Equation solution (e.g., "5 + 6 = 11")
    
    # Source information
    source: Mapped[str] = mapped_column(String(255), default="GuaranIA")
    
    # MD5 hash for content verification
    md5: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    
    # Translation status: true when annotation has 3 translations (one from each of 3 users)
    translated: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - using string names to avoid circular imports
    validations = relationship("AnnotationValidation", back_populates="annotation", cascade="all, delete-orphan")
    suggestions = relationship("AnnotationSuggestion", back_populates="annotation", cascade="all, delete-orphan")
    
    # Many-to-many relationships with users
    assignments = relationship("AnnotationAssignment", back_populates="annotation", cascade="all, delete-orphan")
    translations = relationship("AnnotationTranslation", back_populates="annotation", cascade="all, delete-orphan")
