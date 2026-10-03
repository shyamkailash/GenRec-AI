from unittest.mock import Mock

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from experiments.models import Experiment
from agents.services.retrieval_agent import (
    RetrievalAgent,
    RetrievalAgentError,
)


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

        response_data = result.to_dict()

        self.assertIn("citations", response_data)
        self.assertEqual(len(response_data["citations"]), 2)

        first_citation = response_data["citations"][0]
        self.assertEqual(first_citation["citation_id"], "C1")
        self.assertEqual(first_citation["source"], "ml_manual.pdf")
        self.assertEqual(first_citation["similarity"], 0.91)

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
