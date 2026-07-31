"""Tests for planner routing, observation extraction, planning, and retrieval."""

from unittest.mock import Mock

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from documents.models import ExperimentDocument
from experiments.models import Experiment

from .domain import AgentRoute
from .services import PlannerAgent, PlannerError
from .services.experiment_planner import (
    ExperimentPlanningAgent,
    ExperimentPlanningError,
)
from .services.observation_extractor import (
    ObservationExtractionError,
    extract_observation_sections,
)
from .services.retrieval_agent import (
    RetrievalAgent,
    RetrievalAgentError,
)


class ObservationExtractionAgentTests(SimpleTestCase):
    def test_extracts_observation_sections(self):
        raw_text = """
        Experiment No: 4
        Subject: Machine Learning Laboratory
        Title: Linear Regression

        Aim:
        To implement linear regression.

        Theory:
        Linear regression predicts continuous values.

        Algorithm:
        1. Load the dataset.
        2. Train the model.
        3. Predict the output.

        Procedure:
        Import libraries and execute the program.

        Program:
        print("Linear Regression")
        """

        result = extract_observation_sections(raw_text)

        self.assertEqual(result.experiment_number, "4")
        self.assertEqual(
            result.subject,
            "Machine Learning Laboratory",
        )
        self.assertEqual(
            result.title,
            "Linear Regression",
        )
        self.assertIn(
            "implement linear regression",
            result.aim.lower(),
        )
        self.assertEqual(result.missing_sections, [])

    def test_identifies_missing_sections(self):
        raw_text = """
        Title: Decision Tree

        Aim:
        To implement decision tree classification.
        """

        result = extract_observation_sections(raw_text)

        self.assertIn(
            "algorithm",
            result.missing_sections,
        )
        self.assertIn(
            "procedure",
            result.missing_sections,
        )

    def test_rejects_empty_text(self):
        with self.assertRaises(
            ObservationExtractionError
        ):
            extract_observation_sections("")


class PlannerAgentTests(TestCase):
    def setUp(self):
        self.planner = PlannerAgent()

    def test_routes_new_experiment_to_experiment_planning(self):
        experiment = Experiment.objects.create(
            subject="Python",
            title="Sorting",
        )

        plan = self.planner.plan(experiment)

        self.assertEqual(
            plan.next_agent,
            AgentRoute.EXPERIMENT_PLANNING,
        )

        self.assertEqual(
            [step.agent for step in plan.steps],
            [
                AgentRoute.EXPERIMENT_PLANNING,
                AgentRoute.RETRIEVAL,
                AgentRoute.CONTENT_GENERATION,
                AgentRoute.VALIDATION,
            ],
        )

    def test_routes_generated_experiment_to_validation(self):
        experiment = Experiment.objects.create(
            subject="Python",
            title="Sorting",
            theory="Theory",
            algorithm="Algorithm",
            program="print('sorted')",
            output="sorted",
            result="Successful",
            status="generated",
        )

        plan = self.planner.plan(experiment)

        self.assertEqual(
            plan.next_agent,
            AgentRoute.VALIDATION,
        )

    def test_rejects_missing_required_identity(self):
        experiment = Experiment.objects.create(
            subject=" ",
            title="Sorting",
        )

        with self.assertRaises(
            PlannerError
        ):
            self.planner.plan(experiment)


class PlannerAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.experiment = Experiment.objects.create(
            subject="Data Structures",
            title="Stack",
        )

    def test_returns_serialized_plan(self):
        response = self.client.post(
            reverse("agents:plan"),
            {
                "experiment_id": self.experiment.pk,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["experiment_id"],
            self.experiment.pk,
        )
        self.assertEqual(
            response.data["next_agent"],
            "experiment_planning",
        )

    def test_returns_not_found_for_unknown_experiment(self):
        response = self.client.post(
            reverse("agents:plan"),
            {
                "experiment_id": 99999,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_validates_request(self):
        response = self.client.post(
            reverse("agents:plan"),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class ExperimentPlanningAgentTests(TestCase):
    def setUp(self):
        self.agent = ExperimentPlanningAgent()

    def test_creates_machine_learning_plan(self):
        experiment = Experiment.objects.create(
            subject="Machine Learning Laboratory",
            title="Linear Regression",
            aim="To implement linear regression.",
        )

        plan = self.agent.plan(experiment)

        self.assertEqual(
            plan.experiment_type,
            "machine_learning",
        )
        self.assertEqual(
            plan.programming_language,
            "python",
        )
        self.assertTrue(plan.requires_dataset)

        self.assertIn(
            "theory",
            plan.missing_sections,
        )
        self.assertNotIn(
            "aim",
            plan.missing_sections,
        )

    def test_reads_sections_from_observation(self):
        experiment = Experiment.objects.create(
            subject="Computer Vision Laboratory",
            title="Canny Edge Detection",
        )

        ExperimentDocument.objects.create(
            experiment=experiment,
            document_type="observation",
            file="test/observation.txt",
            extraction_status="completed",
            structure_status="completed",
            structured_content={
                "aim": "To detect object boundaries.",
                "algorithm": "Apply the Canny operator.",
                "procedure": "Load and process the image.",
            },
        )

        plan = self.agent.plan(experiment)

        self.assertIn(
            "aim",
            plan.existing_sections,
        )
        self.assertIn(
            "algorithm",
            plan.existing_sections,
        )
        self.assertIn(
            "procedure",
            plan.existing_sections,
        )

        self.assertNotIn(
            "aim",
            plan.missing_sections,
        )

    def test_rejects_missing_subject(self):
        experiment = Experiment.objects.create(
            subject="",
            title="Sample Experiment",
        )

        with self.assertRaises(
            ExperimentPlanningError
        ):
            self.agent.plan(experiment)


class RetrievalAgentTests(TestCase):
    def test_retrieves_and_ranks_context(self):
        experiment = Experiment.objects.create(
            subject="Machine Learning Laboratory",
            title="Linear Regression",
        )

        fake_search = Mock(
            return_value=[
                {
                    "text": (
                        "Linear regression predicts "
                        "continuous values."
                    ),
                    "similarity": 0.91,
                    "metadata": {
                        "filename": "ml_manual.pdf",
                    },
                },
                {
                    "text": (
                        "The model minimizes prediction error."
                    ),
                    "similarity": 0.82,
                    "metadata": {
                        "filename": "faculty_notes.pdf",
                    },
                },
            ]
        )

        agent = RetrievalAgent(
            search_function=fake_search
        )

        result = agent.retrieve(
            experiment,
            limit_per_query=2,
        )

        self.assertGreater(
            len(result.matches),
            0,
        )
        self.assertEqual(
            result.matches[0].similarity,
            0.91,
        )
        self.assertIn(
            "ml_manual.pdf",
            result.context,
        )

    def test_removes_duplicate_results(self):
        experiment = Experiment.objects.create(
            subject="Python Laboratory",
            title="Sorting",
        )

        duplicate_result = {
            "text": "Bubble sort compares adjacent values.",
            "similarity": 0.85,
            "metadata": {
                "filename": "python_manual.pdf",
            },
        }

        fake_search = Mock(
            return_value=[
                duplicate_result,
                duplicate_result,
            ]
        )

        agent = RetrievalAgent(
            search_function=fake_search
        )

        result = agent.retrieve(experiment)

        self.assertEqual(
            len(result.matches),
            1,
        )

    def test_rejects_invalid_limit(self):
        experiment = Experiment.objects.create(
            subject="Python Laboratory",
            title="Sorting",
        )

        agent = RetrievalAgent(
            search_function=Mock(
                return_value=[]
            )
        )

        with self.assertRaises(
            RetrievalAgentError
        ):
            agent.retrieve(
                experiment,
                limit_per_query=0,
            )


class RetrievalAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.experiment = Experiment.objects.create(
            subject="Python Laboratory",
            title="Bubble Sort",
        )

    def test_validates_retrieval_request(self):
        response = self.client.post(
            reverse("agents:retrieve"),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_returns_not_found_for_unknown_experiment(self):
        response = self.client.post(
            reverse("agents:retrieve"),
            {
                "experiment_id": 99999,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )