"""Validation agent for generated laboratory records."""

from dataclasses import dataclass
from typing import List

from experiments.models import Experiment


class ValidationError(Exception):
    """Raised when validation cannot be performed."""


@dataclass
class ValidationResult:
    is_valid: bool
    score: int
    missing_sections: List[str]
    warnings: List[str]

    def to_dict(self):
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "missing_sections": self.missing_sections,
            "warnings": self.warnings,
        }


class ValidationAgent:
    """Validate generated experiment content."""

    REQUIRED_FIELDS = [
        "aim",
        "theory",
        "algorithm",
        "procedure",
        "program",
        "output",
        "result",
    ]

    def validate(self, experiment: Experiment) -> ValidationResult:
        if experiment is None:
            raise ValidationError("Experiment is required.")

        missing = []
        warnings = []

        score = 100

        for field in self.REQUIRED_FIELDS:
            value = getattr(experiment, field, "")

            if value is None or not str(value).strip():
                missing.append(field)
                score -= 10

        if len(missing) >= 4:
            warnings.append(
                "Large portions of the experiment are missing."
            )

        if experiment.subject.strip() == "":
            warnings.append("Subject is missing.")
            score -= 10

        if experiment.title.strip() == "":
            warnings.append("Title is missing.")
            score -= 10

        score = max(score, 0)

        return ValidationResult(
            is_valid=len(missing) == 0,
            score=score,
            missing_sections=missing,
            warnings=warnings,
        )