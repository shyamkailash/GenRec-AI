from django.test import TestCase

from documents.models import ExperimentDocument
from experiments.models import Experiment
from agents.services.experiment_planner import (
    ExperimentPlanningAgent,
    ExperimentPlanningError,
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
