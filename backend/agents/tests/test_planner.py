from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from experiments.models import Experiment
from agents.domain import AgentRoute
from agents.services import PlannerAgent, PlannerError


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
