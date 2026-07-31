"""Retrieve grounded laboratory knowledge from ChromaDB."""

from experiments.models import Experiment
from rag.services.vector_store import (
    RAGServiceError,
    semantic_search,
)

from agents.retrieval_domain import (
    RetrievalMatch,
    RetrievalResult,
)
from agents.services.experiment_planner import (
    ExperimentPlanningAgent,
)


class RetrievalAgentError(Exception):
    """Raised when retrieval cannot be completed."""


class RetrievalAgent:
    def __init__(
        self,
        planning_agent=None,
        search_function=None,
    ):
        self.planning_agent = (
            planning_agent or ExperimentPlanningAgent()
        )
        self.search_function = (
            search_function or semantic_search
        )

    def retrieve(
        self,
        experiment: Experiment,
        limit_per_query: int = 3,
    ) -> RetrievalResult:
        if not experiment.pk:
            raise RetrievalAgentError(
                "Experiment must be saved before retrieval."
            )

        if limit_per_query < 1 or limit_per_query > 10:
            raise RetrievalAgentError(
                "limit_per_query must be between 1 and 10."
            )

        plan = self.planning_agent.plan(experiment)

        result = RetrievalResult(
            experiment_id=experiment.pk,
            queries=plan.rag_queries,
        )

        seen_content: set[str] = set()

        for query in plan.rag_queries:
            try:
                search_results = self.search_function(
                    query=query,
                    experiment_id=experiment.pk,
                    limit=limit_per_query,
                )
            except RAGServiceError as exc:
                result.warnings.append(
                    f"Retrieval failed for '{query}': {exc}"
                )
                continue
            except Exception as exc:
                result.warnings.append(
                    f"Unexpected retrieval failure for "
                    f"'{query}': {exc}"
                )
                continue

            for item in search_results:
                text = str(
                    item.get("text", "")
                ).strip()

                if not text:
                    continue

                normalized_text = " ".join(
                    text.lower().split()
                )

                if normalized_text in seen_content:
                    continue

                seen_content.add(normalized_text)

                result.matches.append(
                    RetrievalMatch(
                        query=query,
                        text=text,
                        similarity=float(
                            item.get("similarity", 0.0)
                        ),
                        metadata=item.get(
                            "metadata",
                            {},
                        ),
                    )
                )

        result.matches.sort(
            key=lambda match: match.similarity,
            reverse=True,
        )

        result.context = self._build_context(
            result.matches
        )

        if not result.matches:
            result.warnings.append(
                "No relevant RAG context was retrieved."
            )

        return result

    def _build_context(
        self,
        matches: list[RetrievalMatch],
    ) -> str:
        context_blocks = []

        for index, match in enumerate(
            matches,
            start=1,
        ):
            source = match.metadata.get(
                "filename",
                "Unknown source",
            )

            context_blocks.append(
                "\n".join(
                    [
                        f"[Context {index}]",
                        f"Source: {source}",
                        (
                            "Similarity: "
                            f"{match.similarity:.4f}"
                        ),
                        match.text,
                    ]
                )
            )

        return "\n\n".join(context_blocks)