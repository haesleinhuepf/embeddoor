"""Provider initialization for embeddings."""

from embeddoor.embeddings.providers.huggingface import HuggingFaceEmbedding
from embeddoor.embeddings.providers.openai_provider import OpenAIEmbedding
from embeddoor.embeddings.providers.gemini import GeminiEmbedding

# Try to import CLIP provider (may not be available if transformers not installed)
try:
    from embeddoor.embeddings.providers.clip_provider import CLIPImageEmbedder
    __all__ = [
        'HuggingFaceEmbedding',
        'OpenAIEmbedding',
        'GeminiEmbedding',
        'CLIPImageEmbedder',
    ]
except ImportError:
    __all__ = [
        'HuggingFaceEmbedding',
        'OpenAIEmbedding',
        'GeminiEmbedding',
    ]
