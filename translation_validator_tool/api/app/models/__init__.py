# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .translation import Translation
from .validation import Validation
from .suggestion import TranslationSuggestion

__all__ = ["User", "Translation", "Validation", "TranslationSuggestion"]