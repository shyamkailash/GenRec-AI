"""Tests for Workflow Orchestrator."""

from django.test import SimpleTestCase

from agents.services.workflow.workflow_factory import WorkflowFactory
from agents.services.workflow.workflow_executor import WorkflowExecutor
from agents.services.workflow.workflow_orchestrator import WorkflowOrchestrator
from agents.services.workflow.workflow_state import WorkflowState
from agents.services.workflow.workflow_exceptions import WorkflowError


class WorkflowInitializationTests(SimpleTestCase):
    """Workflow initialization tests."""

    def test_workflow_initialization(self):
        workflow = WorkflowOrchestrator()

        self.assertIsNotNone(workflow)


class WorkflowStateTests(SimpleTestCase):
    """Workflow state tests."""

    def test_state_creation(self):
        state = WorkflowState(
            experiment_id=1,
            current_agent="planner",
        )

        self.assertEqual(state.experiment_id, 1)
        self.assertEqual(state.current_agent, "planner")


class WorkflowFactoryTests(SimpleTestCase):
    """Workflow factory tests."""

    def test_factory_creates_workflow(self):
        workflow = WorkflowFactory.create()

        self.assertIsInstance(
            workflow,
            WorkflowOrchestrator,
        )


class WorkflowExecutorTests(SimpleTestCase):
    """Workflow executor tests."""

    def setUp(self):
        self.executor = WorkflowExecutor()

    def test_workflow_execution(self):
        state = WorkflowState(
            experiment_id=1,
            current_agent="planner",
        )

        result = self.executor.execute(state)

        self.assertIsNotNone(result)

    def test_invalid_workflow(self):
        with self.assertRaises(WorkflowError):
            self.executor.execute(None)


class WorkflowCompletionTests(SimpleTestCase):
    """Workflow completion tests."""

    def test_workflow_completion(self):
        state = WorkflowState(
            experiment_id=1,
            current_agent="validation",
        )

        state.completed = True

        self.assertTrue(state.completed)