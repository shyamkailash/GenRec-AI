"""
Content Generation Agent.

Uses retrieved knowledge and experiment metadata to generate
the missing laboratory record sections.
"""

from dataclasses import dataclass

from experiments.models import Experiment


class ContentGenerationError(Exception):
    """Raised when generation cannot proceed."""


@dataclass(slots=True)
class GeneratedContent:
    theory: str = ""
    algorithm: str = ""
    procedure: str = ""
    program: str = ""
    output: str = ""
    result: str = ""


class ContentGenerationAgent:
    """
    Builds laboratory-record content from
    experiment metadata and retrieved references.
    """

    REQUIRED_FIELDS = (
        "subject",
        "title",
    )

    def generate(
        self,
        experiment: Experiment,
        retrieved_context: str,
    ) -> GeneratedContent:

        for field in self.REQUIRED_FIELDS:
            value = getattr(experiment, field, "")
            if not value or not str(value).strip():
                raise ContentGenerationError(
                    f"Experiment {field} is required."
                )

        if not retrieved_context.strip():
            raise ContentGenerationError(
                "Retrieved context is empty."
            )

        title = experiment.title

        return GeneratedContent(
            theory=(
                f"Theory for {title}.\n\n"
                + retrieved_context[:600]
            ),
            algorithm=(
                "1. Read input.\n"
                "2. Process data.\n"
                "3. Produce output."
            ),
            procedure=(
                "Follow the laboratory procedure "
                "using the supplied dataset."
            ),
            program=(
                "# Program placeholder\n"
                "print('Generated Program')"
            ),
            output="Expected output generated.",
            result="Experiment executed successfully.",
        )