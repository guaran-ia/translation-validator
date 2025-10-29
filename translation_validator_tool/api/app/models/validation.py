from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Validation(Base):
    __tablename__ = "validations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    translation_id: Mapped[int] = mapped_column(ForeignKey("translations.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    correctness: Mapped[str] = mapped_column(String(20))  # "correct", "gn_more", "es_more", "incorrect"
    fluency_score: Mapped[int] = mapped_column(Integer)  # 1-5
    accuracy_score: Mapped[int] = mapped_column(Integer)  # 1-5
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    direction: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    # If non-null, this validation is validating a suggestion rather than the translation itself
    suggestion_id: Mapped[Optional[int]] = mapped_column(ForeignKey("translation_suggestions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - using string names to avoid circular imports
    translation = relationship("Translation", back_populates="validations")
    user = relationship("User", back_populates="validations")
    suggestion = relationship("TranslationSuggestion", back_populates="validations")
    
    # Constraint: Un usuario solo puede validar una vez cada traducción
    __table_args__ = (UniqueConstraint('translation_id', 'user_id', name='unique_user_translation'),)