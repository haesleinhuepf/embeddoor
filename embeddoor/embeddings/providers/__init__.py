"""Provider initialization for embeddings."""

from embeddoor.embeddings.providers.huggingface import HuggingFaceEmbedding
from embeddoor.embeddings.providers.openai_provider import OpenAIEmbedding
from embeddoor.embeddings.providers.gemini import GeminiEmbedding

__all__ = [
    'HuggingFaceEmbedding',
    'OpenAIEmbedding',
    'GeminiEmbedding',
]
