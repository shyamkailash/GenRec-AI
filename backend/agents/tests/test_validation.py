from django.test import TestCase

from experiments.models import Experiment
from agents.services.validation_agent import (
    ValidationAgent,
    ValidationError,
)


class ValidationAgentTests(TestCase):
    def setUp(self):
        self.agent = ValidationAgent()

    def test_valid_experiment(self):
        experiment = Experiment.objects.create(
            subject="Machine Learning",
            title="Linear Regression",
            aim="Aim",
            theory="Theory",
            algorithm="Algorithm",
            procedure="Procedure",
            program="print('Hello')",
            output="Output",
            result="Success",
        )

        result = self.agent.validate(experiment)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.score, 100)
        self.assertEqual(result.missing_sections, [])

    def test_missing_sections(self):
        experiment = Experiment.objects.create(
            subject="Machine Learning",
            title="Linear Regression",
        )

        result = self.agent.validate(experiment)

        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.missing_sections), 0)

    def test_none_experiment(self):
        with self.assertRaises(ValidationError):
            self.agent.validate(None)