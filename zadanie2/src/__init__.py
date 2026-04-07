"""Adversarial Prompt Generation Pipeline
Модульная система для генерации adversarial промптов"""

from .generator import apply_templates
from .noise import mixed_noise, heavy_noise
from .dedup import quick_deduplicate, SemanticDeduplicator
from .classify import DifficultyClassifier
from .llm import create_paraphraser, LLMParaphraser, create_local_paraphraser

__version__ = "1.0.0"
__all__ = [
    "apply_templates",
    "mixed_noise", 
    "heavy_noise",
    "quick_deduplicate",
    "SemanticDeduplicator",
    "DifficultyClassifier",
    "create_paraphraser",
    "LLMParaphraser",
    "create_local_paraphraser"
]
