"""
AnnotationValidation model for storing validation feedback on question-answer translations.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AnnotationValidation(Base):
    __tablename__ = "annotation_validations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    annotation_id: Mapped[int] = mapped_column(ForeignKey("annotations.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Which part is being validated: "question", "answer", or "both"
    part_type: Mapped[str] = mapped_column(String(20), default="both")
    
    # Correctness evaluation
    correctness: Mapped[str] = mapped_column(String(20))  # "correct", "minor_issues", "major_issues", "incorrect"
    
    # Quality scores (1-5)
    fluency_score: Mapped[int] = mapped_column(Integer)  # How natural the translation sounds
    accuracy_score: Mapped[int] = mapped_column(Integer)  # How accurately it conveys the meaning
    
    # Notes and feedback
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # If non-null, this validation is validating a suggestion rather than the translation itself
    suggestion_id: Mapped[Optional[int]] = mapped_column(ForeignKey("annotation_suggestions.id"), nullable=True)
    
    # Category for Guarani classification (guarani_puro, jopara, jehea)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - using string names to avoid circular imports
    annotation = relationship("Annotation", back_populates="validations")
    user = relationship("User", back_populates="annotation_validations")
    suggestion = relationship("AnnotationSuggestion", back_populates="validations")
    
    # Constraint: Un usuario solo puede validar una vez cada anotación (por parte)
    __table_args__ = (UniqueConstraint('annotation_id', 'user_id', 'part_type', name='unique_user_annotation_part'),)
