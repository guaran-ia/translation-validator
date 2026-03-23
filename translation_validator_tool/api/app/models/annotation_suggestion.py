"""
AnnotationSuggestion model for storing translation suggestions for question-answer pairs.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Text, ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AnnotationSuggestion(Base):
    __tablename__ = "annotation_suggestions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    annotation_id: Mapped[int] = mapped_column(ForeignKey("annotations.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Which part is being suggested: "question", "answer", or "both"
    part_type: Mapped[str] = mapped_column(String(20), default="both")
    
    # Suggested translations (depending on part_type, one or both will be populated)
    suggested_question_gn: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suggested_answer_gn: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Reason for suggestion
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Track if this suggestion was promoted to official translation
    is_promoted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - using string names to avoid circular imports
    annotation = relationship("Annotation", back_populates="suggestions")
    user = relationship("User", back_populates="annotation_suggestions")
    # Validations that refer to this suggestion
    validations = relationship("AnnotationValidation", back_populates="suggestion")
