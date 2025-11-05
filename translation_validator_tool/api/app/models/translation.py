from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from sqlalchemy import Integer, Boolean, ForeignKey


class Translation(Base):
    __tablename__ = "translations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    guarani_text: Mapped[str] = mapped_column(Text)
    spanish_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Allow null for sentences without translation
    source: Mapped[str] = mapped_column(String(255), default="jojajovai")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    # Direction of translation: 'sp-gn' means Spanish -> Guarani (default), 'gn-sp' means Guarani -> Spanish
    direction: Mapped[str] = mapped_column(String(10), nullable=False, default='sp-gn')
    # Pairing to the inverse record (optional)
    pair_id: Mapped[Optional[int]] = mapped_column(ForeignKey('translations.id'), nullable=True)
    is_original: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships - using string names to avoid circular imports
    validations = relationship("Validation", back_populates="translation", cascade="all, delete-orphan")
    suggestions = relationship("TranslationSuggestion", back_populates="translation", cascade="all, delete-orphan")