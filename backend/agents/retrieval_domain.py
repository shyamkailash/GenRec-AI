"""Typed domain objects for retrieval-agent output."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RetrievalMatch:
    query: str
    text: str
    similarity: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RetrievalResult:
    experiment_id: int
    queries: list[str]
    matches: list[RetrievalMatch] = field(default_factory=list)
    context: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        citations = []

        for index, match in enumerate(self.matches, start=1):
            metadata = match.metadata or {}

            citations.append({
                "citation_id": f"C{index}",
                "source": metadata.get("filename") or "Unknown source",
                "document_id": metadata.get("document_id"),
                "experiment_id": metadata.get(
                    "experiment_id", self.experiment_id
                ),
                "chunk_index": metadata.get("chunk_index"),
                "similarity": match.similarity,
                "query": match.query,
            })

        return {
            "experiment_id": self.experiment_id,
            "queries": self.queries,
            "matches": [
                match.to_dict()
                for match in self.matches
            ],
            "context": self.context,
            "warnings": self.warnings,
            "citations": citations,
        }
