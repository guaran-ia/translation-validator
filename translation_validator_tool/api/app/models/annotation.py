"""
Annotation model for storing question-answer pairs with translations.
Each annotation consists of:
- A question in Spanish (question_es) that can be translated to Guaraní (question_gn)
- An answer in Spanish (answer_es) that can be translated to Guaraní (answer_gn)
- Metadata: answer_number, equation_solution
- Assignment: assigned_to_user_id (translator assigned to this annotation)
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Annotation(Base):
    __tablename__ = "annotations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Question fields (optional for translation)
    question_es: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Original question in Spanish
    question_gn: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Translated question in Guaraní
    
    # Answer fields (optional for translation)
    answer_es: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Original answer in Spanish
    answer_gn: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Translated answer in Guaraní
    
    # Metadata fields
    answer_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Numeric answer (e.g., 18)
    equation_solution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Equation solution (e.g., "5 + 6 = 11")
    
    # Source information
    source: Mapped[str] = mapped_column(String(255), default="GuaranIA")
    
    # Assignment: which translator is assigned to this annotation
    assigned_to_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Translation status: whether both question_gn and answer_gn have been filled
    translated: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - using string names to avoid circular imports
    validations = relationship("AnnotationValidation", back_populates="annotation", cascade="all, delete-orphan")
    suggestions = relationship("AnnotationSuggestion", back_populates="annotation", cascade="all, delete-orphan")
    assigned_to_user = relationship("User", back_populates="assigned_annotations")
