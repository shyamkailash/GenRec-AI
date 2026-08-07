from django.test import TestCase
from experiments.models import Experiment
from agents.services.document_generation import (
    DocumentGenerationAgent,
    DocumentGenerationError,
)


class DocumentGenerationAgentTests(TestCase):
    def setUp(self):
        self.agent = DocumentGenerationAgent()

    def test_generates_documents(self):
        experiment = Experiment.objects.create(
            subject="Operating Systems",
            title="SJF Scheduling",
            aim="To implement SJF scheduling.",
            theory="Shortest Job First scheduling.",
            algorithm="1. Sort jobs by burst time.",
            procedure="Run jobs accordingly.",
            program="print('SJF')",
            output="SJF execution",
            result="Success",
        )

        result = self.agent.generate(experiment)

        self.assertEqual(result.experiment_id, experiment.pk)
        self.assertEqual(result.status, "completed")
        self.assertTrue(experiment.generated_pdf)
        self.assertTrue(experiment.generated_docx)
        self.assertEqual(experiment.status, "validated")

    def test_rejects_unsaved_experiment(self):
        experiment = Experiment(
            subject="OS",
            title="Unsaved",
        )

        with self.assertRaises(DocumentGenerationError):
            self.agent.generate(experiment)
