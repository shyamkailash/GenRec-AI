from django.test import TestCase

from experiments.models import Experiment

from agents.services.content_generator import (
    ContentGenerationAgent,
    ContentGenerationError,
)


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