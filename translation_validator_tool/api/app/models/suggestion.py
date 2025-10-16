from datetime import datetime
from typing import Optional
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TranslationSuggestion(Base):
    __tablename__ = "translation_suggestions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    translation_id: Mapped[int] = mapped_column(ForeignKey("translations.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    suggested_guarani: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suggested_spanish: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships - using string names to avoid circular imports
    translation = relationship("Translation", back_populates="suggestions")
    user = relationship("User", back_populates="suggestions")