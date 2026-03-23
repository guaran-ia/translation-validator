# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .translation import Translation
from .validation import Validation
from .suggestion import TranslationSuggestion
from .annotation import Annotation
from .annotation_validation import AnnotationValidation
from .annotation_suggestion import AnnotationSuggestion

__all__ = [
    "User",
    "Translation",
    "Validation",
    "TranslationSuggestion",
    "Annotation",
    "AnnotationValidation",
    "AnnotationSuggestion",
]