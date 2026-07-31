"""Domain objects shared by the agent orchestration layer."""

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class AgentRoute(StrEnum):
    """Valid destinations selected by the planner agent."""

    OBSERVATION_EXTRACTION = "observation_extraction"
    EXPERIMENT_PLANNING = "experiment_planning"
    RETRIEVAL = "retrieval"
    CONTENT_GENERATION = "content_generation"
    VALIDATION = "validation"
    DOCUMENT_GENERATION = "document_generation"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    """One executable step in a generated workflow plan."""

    agent: AgentRoute
    reason: str


@dataclass(frozen=True, slots=True)
class WorkflowPlan:
    """Planner output returned to API and orchestration callers."""

    experiment_id: int
    next_agent: AgentRoute
    steps: tuple[WorkflowStep, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the plan."""

        return asdict(self)
