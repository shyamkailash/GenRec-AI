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
