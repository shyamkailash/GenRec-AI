"""Public services for indexing and searching the RAG knowledge base."""

from .vector_store import (
    RAGServiceError,
    chunk_text,
    delete_document_index,
    get_chroma_client,
    get_collection,
    get_embedding_model,
    index_document,
    semantic_search,
)

__all__ = [
    "RAGServiceError",
    "chunk_text",
    "delete_document_index",
    "get_chroma_client",
    "get_collection",
    "get_embedding_model",
    "index_document",
    "semantic_search",
]
