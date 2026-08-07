"""Shared workflow state passed between all agents."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from experiments.models import Experiment


@dataclass
class WorkflowState:
    """
    Shared state object used throughout the workflow.
    """

    experiment: Experiment | None = None
    experiment_id: int | None = None
    current_agent: str = "planner"
    completed_agents: list[str] = field(default_factory=list)
    results: dict[str, Any] = field(default_factory=dict)
    failed: bool = False
    error: str = ""
    finished: bool = False
    completed: bool = False
    status: str = "initialized"
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None

    # Intermediate agent results / context
    planner_plan: Any | None = None
    experiment_plan: Any | None = None
    retrieval_context: list[Any] = field(default_factory=list)
    generated_content: dict[str, Any] = field(default_factory=dict)
    validation_result: Any | None = None
    document_result: Any | None = None

    def __post_init__(self):
        if self.experiment is not None:
            if self.experiment_id is None:
                self.experiment_id = self.experiment.id
        elif self.experiment_id is not None:
            pass

    def move_next(self):
        """Transition current_agent to the next workflow step."""
        agents_order = [
            "observation_extraction",
            "planner",
            "experiment_planner",
            "retrieval",
            "content_generation",
            "validation",
            "document_generation",
        ]

        if self.planner_plan and hasattr(self.planner_plan, "steps") and self.planner_plan.steps:
            plan_agents = [str(step.agent) for step in self.planner_plan.steps]
            try:
                current_idx = plan_agents.index(self.current_agent)
                if current_idx + 1 < len(plan_agents):
                    self.current_agent = plan_agents[current_idx + 1]
                    return
                else:
                    self.finished = True
                    self.completed = True
                    self.status = "completed"
                    self.finished_at = datetime.utcnow()
                    return
            except ValueError:
                if plan_agents:
                    self.current_agent = plan_agents[0]
                    return

        try:
            current_idx = agents_order.index(self.current_agent)
            if current_idx + 1 < len(agents_order):
                self.current_agent = agents_order[current_idx + 1]
            else:
                self.finished = True
                self.completed = True
                self.status = "completed"
                self.finished_at = datetime.utcnow()
        except ValueError:
            self.finished = True
            self.status = "failed"
            self.finished_at = datetime.utcnow()