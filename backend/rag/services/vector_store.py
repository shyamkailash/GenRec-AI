"""Persistent ChromaDB storage using explicit SentenceTransformer embeddings."""

from functools import lru_cache
from typing import Any

import chromadb
from django.conf import settings
from sentence_transformers import SentenceTransformer


class RAGServiceError(Exception):
    """Raised when RAG indexing or retrieval cannot be completed safely."""


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the configured local sentence embedding model."""

    try:
        return SentenceTransformer(settings.RAG_EMBEDDING_MODEL)
    except Exception as exc:
        raise RAGServiceError(f"Unable to load embedding model: {exc}") from exc


@lru_cache(maxsize=1)
def get_chroma_client() -> Any:
    """Create and cache the persistent ChromaDB client."""

    try:
        return chromadb.PersistentClient(path=str(settings.CHROMA_DB_PATH))
    except Exception as exc:
        raise RAGServiceError(f"Unable to initialize ChromaDB: {exc}") from exc


@lru_cache(maxsize=1)
def get_collection() -> Any:
    """Return the collection shared by indexing and semantic retrieval."""

    try:
        return get_chroma_client().get_or_create_collection(
            name=settings.RAG_COLLECTION_NAME,
            metadata={
                "description": "GenRec-AI laboratory knowledge base",
                "hnsw:space": "cosine",
            },
        )
    except RAGServiceError:
        raise
    except Exception as exc:
        raise RAGServiceError(f"Unable to access ChromaDB collection: {exc}") from exc


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """Split text into overlapping, non-empty character chunks."""

    normalized_text = text.strip()
    if not normalized_text:
        return []

    resolved_size = chunk_size or settings.RAG_CHUNK_SIZE
    resolved_overlap = (
        settings.RAG_CHUNK_OVERLAP if overlap is None else overlap
    )
    if resolved_size < 1:
        raise RAGServiceError("chunk_size must be greater than zero.")
    if resolved_overlap < 0 or resolved_overlap >= resolved_size:
        raise RAGServiceError("overlap must be non-negative and smaller than chunk_size.")

    step = resolved_size - resolved_overlap
    return [
        normalized_text[start : start + resolved_size].strip()
        for start in range(0, len(normalized_text), step)
        if normalized_text[start : start + resolved_size].strip()
    ]


def index_document(document: Any) -> int:
    """Replace a document's existing chunks and return the indexed chunk count."""

    if not getattr(document, "pk", None):
        raise RAGServiceError("Document must be saved before it can be indexed.")

    chunks = chunk_text(str(getattr(document, "extracted_text", "")))
    if not chunks:
        raise RAGServiceError("Document has no extracted text to index.")

    try:
        collection = get_collection()
        model = get_embedding_model()
        embeddings = _encode(model, chunks)
        document_id = int(document.pk)
        experiment_id = int(document.experiment_id)
        filename = str(document.original_filename or document.file.name)
        metadatas = [
            {
                "document_id": document_id,
                "experiment_id": experiment_id,
                "filename": filename,
                "document_type": str(document.document_type),
                "chunk_index": index,
            }
            for index in range(len(chunks))
        ]

        collection.delete(where={"document_id": document_id})
        collection.add(
            ids=[f"document-{document_id}-chunk-{index}" for index in range(len(chunks))],
            documents=chunks,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return len(chunks)
    except RAGServiceError:
        raise
    except Exception as exc:
        raise RAGServiceError(f"Document indexing failed: {exc}") from exc


def delete_document_index(document_id: int) -> None:
    """Remove every indexed chunk belonging to one source document."""

    if document_id < 1:
        raise RAGServiceError("document_id must be a positive integer.")
    try:
        get_collection().delete(where={"document_id": document_id})
    except RAGServiceError:
        raise
    except Exception as exc:
        raise RAGServiceError(f"Unable to delete document index: {exc}") from exc


def semantic_search(
    query: str,
    experiment_id: int | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Return the most similar indexed chunks for a validated query."""

    normalized_query = query.strip()
    if not normalized_query:
        raise RAGServiceError("Search query cannot be empty.")
    if limit < 1 or limit > 20:
        raise RAGServiceError("limit must be between 1 and 20.")
    if experiment_id is not None and experiment_id < 1:
        raise RAGServiceError("experiment_id must be a positive integer.")

    try:
        collection = get_collection()
        collection_size = collection.count()
        if collection_size == 0:
            return []

        query_arguments: dict[str, Any] = {
            "query_embeddings": _encode(get_embedding_model(), [normalized_query]),
            "n_results": min(limit, collection_size),
            "include": ["documents", "metadatas", "distances"],
        }
        if experiment_id is not None:
            query_arguments["where"] = {"experiment_id": experiment_id}

        raw_results = collection.query(**query_arguments)
    except RAGServiceError:
        raise
    except Exception as exc:
        raise RAGServiceError(f"Semantic search failed: {exc}") from exc

    documents = _first_result_list(raw_results, "documents")
    metadatas = _first_result_list(raw_results, "metadatas")
    distances = _first_result_list(raw_results, "distances")
    results: list[dict[str, Any]] = []

    for text, metadata, distance in zip(documents, metadatas, distances):
        numeric_distance = float(distance)
        results.append(
            {
                "text": str(text),
                "metadata": metadata or {},
                "distance": numeric_distance,
                "similarity": max(0.0, min(1.0, 1.0 - numeric_distance)),
            }
        )
    return results


def _encode(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    encoded = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return encoded.tolist() if hasattr(encoded, "tolist") else encoded


def _first_result_list(results: dict[str, Any], key: str) -> list[Any]:
    values = results.get(key) or []
    return values[0] if values else []
