"""Workflow Orchestrator.

Coordinates all AI agents responsible for generating
a laboratory record.
"""

from .workflow_state import WorkflowState
from .workflow_executor import WorkflowExecutor


class WorkflowOrchestrator:
    """
    Executes the end-to-end workflow.
    """

    def __init__(self):
        self.executor = WorkflowExecutor()

    def execute(self, experiment) -> WorkflowState:
        """
        Execute the workflow until finished or failed.

        Parameters
        ----------
        experiment:
            Experiment instance.

        Returns
        -------
        WorkflowState
        """
        state = WorkflowState(experiment=experiment)

        while not state.finished and not state.failed:
            state = self.executor.execute(state)

        return state