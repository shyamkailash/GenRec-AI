"""Tests for planner routing and its REST endpoint."""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from experiments.models import Experiment

from .domain import AgentRoute
from .services import PlannerAgent, PlannerError

from django.test import SimpleTestCase

from agents.services.observation_extractor import (
    ObservationExtractionError,
    extract_observation_sections,
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
        experiment = Experiment.objects.create(subject="Python", title="Sorting")

        plan = self.planner.plan(experiment)

        self.assertEqual(plan.next_agent, AgentRoute.EXPERIMENT_PLANNING)
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

        self.assertEqual(plan.next_agent, AgentRoute.VALIDATION)

    def test_rejects_missing_required_identity(self):
        experiment = Experiment.objects.create(subject=" ", title="Sorting")

        with self.assertRaises(PlannerError):
            self.planner.plan(experiment)


class PlannerAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.experiment = Experiment.objects.create(
            subject="Data Structures", title="Stack"
        )

    def test_returns_serialized_plan(self):
        response = self.client.post(
            reverse("agents:plan"),
            {"experiment_id": self.experiment.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["experiment_id"], self.experiment.pk)
        self.assertEqual(response.data["next_agent"], "experiment_planning")

    def test_returns_not_found_for_unknown_experiment(self):
        response = self.client.post(
            reverse("agents:plan"), {"experiment_id": 99999}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_validates_request(self):
        response = self.client.post(reverse("agents:plan"), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
