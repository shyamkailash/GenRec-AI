from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from experiments.models import Experiment

from agents.services.content_generator import (
    ContentGenerationAgent,
    ContentGenerationError,
    GeneratedContent,
)
from agents.services.retrieval_agent import RetrievalAgentError
from agents.views import ContentGenerationAPIView


class ContentGenerationAgentTests(TestCase):

    def setUp(self):
        self.agent = ContentGenerationAgent()

    def test_generates_content(self):

        experiment = Experiment.objects.create(
            subject="Machine Learning",
            title="Linear Regression",
        )

        result = self.agent.generate(
            experiment,
            "Linear regression is used for prediction.",
        )

        self.assertTrue(result.theory)
        self.assertTrue(result.algorithm)
        self.assertTrue(result.program)

    def test_requires_context(self):

        experiment = Experiment.objects.create(
            subject="ML",
            title="Regression",
        )

        with self.assertRaises(
            ContentGenerationError
        ):
            self.agent.generate(
                experiment,
                "",
            )


class ContentGenerationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.experiment = Experiment.objects.create(
            subject="Machine Learning",
            title="Linear Regression",
        )
        self.url = reverse("agents:generate-content")

    def test_returns_generated_content_and_retrieval_citations(self):
        citations = [
            {
                "citation_id": "C1",
                "source": "ml_manual.pdf",
                "document_id": 12,
                "experiment_id": self.experiment.pk,
                "chunk_index": 3,
                "similarity": 0.91,
                "query": "linear regression",
            }
        ]
        retrieval_result = Mock(
            context="Retrieved regression context."
        )
        retrieval_result.to_dict.return_value = {
            "citations": citations,
        }
        generated_content = GeneratedContent(
            theory="Generated theory.",
            algorithm="Generated algorithm.",
            procedure="Generated procedure.",
            program="Generated program.",
            output="Generated output.",
            result="Generated result.",
        )

        with (
            patch.object(
                ContentGenerationAPIView,
                "retrieval_agent_class",
            ) as retrieval_agent_class,
            patch.object(
                ContentGenerationAPIView,
                "content_agent_class",
            ) as content_agent_class,
        ):
            retrieval_agent_class.return_value.retrieve.return_value = (
                retrieval_result
            )
            content_agent_class.return_value.generate.return_value = (
                generated_content
            )

            response = self.client.post(
                self.url,
                {"experiment_id": self.experiment.pk},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["theory"], "Generated theory.")
        self.assertEqual(response.data["algorithm"], "Generated algorithm.")
        self.assertEqual(response.data["procedure"], "Generated procedure.")
        self.assertEqual(response.data["program"], "Generated program.")
        self.assertEqual(response.data["output"], "Generated output.")
        self.assertEqual(response.data["result"], "Generated result.")
        self.assertEqual(response.data["citations"], citations)
        retrieval_agent_class.return_value.retrieve.assert_called_once()
        generation_call = content_agent_class.return_value.generate.call_args
        self.assertEqual(
            generation_call.kwargs["experiment"].pk,
            self.experiment.pk,
        )
        self.assertEqual(
            generation_call.kwargs["retrieved_context"],
            "Retrieved regression context.",
        )

    def test_supplied_context_skips_retrieval_and_returns_no_citations(self):
        with (
            patch.object(
                ContentGenerationAPIView,
                "retrieval_agent_class",
            ) as retrieval_agent_class,
            patch.object(
                ContentGenerationAPIView,
                "content_agent_class",
            ) as content_agent_class,
        ):
            content_agent_class.return_value.generate.return_value = (
                GeneratedContent(theory="Generated theory.")
            )

            response = self.client.post(
                self.url,
                {
                    "experiment_id": self.experiment.pk,
                    "retrieved_context": "Caller-provided context.",
                },
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["citations"], [])
        retrieval_agent_class.assert_not_called()
        generation_call = content_agent_class.return_value.generate.call_args
        self.assertEqual(
            generation_call.kwargs["experiment"].pk,
            self.experiment.pk,
        )
        self.assertEqual(
            generation_call.kwargs["retrieved_context"],
            "Caller-provided context.",
        )

    def test_retrieval_failure_falls_back_to_generation_without_citations(self):
        with (
            patch.object(
                ContentGenerationAPIView,
                "retrieval_agent_class",
            ) as retrieval_agent_class,
            patch.object(
                ContentGenerationAPIView,
                "content_agent_class",
            ) as content_agent_class,
        ):
            retrieval_agent_class.return_value.retrieve.side_effect = (
                RetrievalAgentError("Retrieval unavailable.")
            )
            content_agent_class.return_value.generate.return_value = (
                GeneratedContent(theory="Generated theory.")
            )

            response = self.client.post(
                self.url,
                {"experiment_id": self.experiment.pk},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["citations"], [])
        retrieval_agent_class.return_value.retrieve.assert_called_once()
        generation_call = content_agent_class.return_value.generate.call_args
        self.assertEqual(
            generation_call.kwargs["experiment"].pk,
            self.experiment.pk,
        )
        self.assertEqual(
            generation_call.kwargs["retrieved_context"],
            "",
        )

    def test_generation_failure_preserves_error_response(self):
        retrieval_result = Mock(context="Retrieved regression context.")
        retrieval_result.to_dict.return_value = {"citations": []}

        with (
            patch.object(
                ContentGenerationAPIView,
                "retrieval_agent_class",
            ) as retrieval_agent_class,
            patch.object(
                ContentGenerationAPIView,
                "content_agent_class",
            ) as content_agent_class,
        ):
            retrieval_agent_class.return_value.retrieve.return_value = (
                retrieval_result
            )
            content_agent_class.return_value.generate.side_effect = (
                ContentGenerationError("Generation failed.")
            )

            response = self.client.post(
                self.url,
                {"experiment_id": self.experiment.pk},
                format="json",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        self.assertEqual(response.data, {"detail": "Generation failed."})
        content_agent_class.return_value.generate.assert_called_once()