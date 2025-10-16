from datetime import datetime
from typing import List
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Translation(Base):
    __tablename__ = "translations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    guarani_text: Mapped[str] = mapped_column(Text)
    spanish_text: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(255), default="jojajovai")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - using string names to avoid circular imports
    validations = relationship("Validation", back_populates="translation", cascade="all, delete-orphan")
    suggestions = relationship("TranslationSuggestion", back_populates="translation", cascade="all, delete-orphan")