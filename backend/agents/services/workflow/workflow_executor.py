"""
Executes a single workflow step.
"""

from .workflow_state import WorkflowState
from .workflow_exceptions import (
    WorkflowError,
    WorkflowStateError,
    ExtractionFailure,
    PlanningFailure,
    RetrievalFailure,
    GenerationFailure,
    ValidationFailure,
    DocumentGenerationFailure,
)
from .workflow_factory import WorkflowFactory

EXCEPTION_MAPPING = {
    "observation_extraction": ExtractionFailure,
    "planner": PlanningFailure,
    "experiment_planner": PlanningFailure,
    "experiment_planning": PlanningFailure,
    "retrieval": RetrievalFailure,
    "content_generation": GenerationFailure,
    "validation": ValidationFailure,
    "document_generation": DocumentGenerationFailure,
}


class WorkflowExecutor:
    """
    Executes one workflow step.
    """

    def __init__(self):
        self.factory = WorkflowFactory()

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the current workflow agent.
        """

        if state is None or not hasattr(state, "finished"):
            raise WorkflowError("Invalid workflow state.")

        if state.finished:
            return state

        agent = self.factory.get_agent(state.current_agent)

        if agent is None:
            raise WorkflowError(
                f"No agent registered for '{state.current_agent}'"
            )

        try:
            result = agent.run(state.experiment, state)

            state.completed_agents.append(state.current_agent)

            state.results[state.current_agent] = result

            state.move_next()

            return state

        except Exception as exc:
            state.failed = True
            state.error = str(exc)

            exception_class = EXCEPTION_MAPPING.get(state.current_agent, WorkflowError)
            raise exception_class(str(exc)) from exc