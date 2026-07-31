"""Deterministic planner for the laboratory-record agent workflow."""

from collections.abc import Iterable

from documents.models import ExperimentDocument
from experiments.models import Experiment

from agents.domain import AgentRoute, WorkflowPlan, WorkflowStep


class PlannerError(Exception):
    """Raised when an experiment cannot safely enter the workflow."""


class PlannerAgent:
    """Inspect experiment state and select the next specialized agent.

    Routing is deliberately deterministic. LLM agents can execute individual
    steps later without being allowed to silently skip required workflow gates.
    """

    GENERATED_FIELDS = ("theory", "algorithm", "program", "output", "result")
    OBSERVATION_FIELDS = ("aim", "theory", "algorithm", "procedure")

    def plan(self, experiment: Experiment) -> WorkflowPlan:
        """Build an ordered plan starting at the experiment's current state."""

        if not experiment.subject.strip() or not experiment.title.strip():
            raise PlannerError("Subject and experiment title are required.")

        documents = tuple(experiment.documents.all())
        failed_documents = self._documents_with_status(documents, "failed")
        pending_observations = tuple(
            document
            for document in documents
            if document.document_type == "observation"
            and document.extraction_status in {"pending", "processing"}
        )
        completed_observations = tuple(
            document
            for document in documents
            if document.document_type == "observation"
            and document.extraction_status == "completed"
            and document.extracted_text.strip()
        )

        warnings = tuple(
            f"Document {document.id} failed extraction: "
            f"{document.extraction_error or 'unknown error'}"
            for document in failed_documents
        )

        steps: list[WorkflowStep] = []
        if pending_observations:
            steps.append(
                WorkflowStep(
                    AgentRoute.OBSERVATION_EXTRACTION,
                    "An uploaded observation is waiting for text extraction.",
                )
            )

        if completed_observations and self._missing(experiment, self.OBSERVATION_FIELDS):
            steps.append(
                WorkflowStep(
                    AgentRoute.OBSERVATION_EXTRACTION,
                    "Extract structured sections from the observation text.",
                )
            )

        if self._missing(experiment, self.GENERATED_FIELDS):
            steps.extend(
                [
                    WorkflowStep(
                        AgentRoute.EXPERIMENT_PLANNING,
                        "Determine required sections, code, flow, and expected output.",
                    ),
                    WorkflowStep(
                        AgentRoute.RETRIEVAL,
                        "Retrieve grounded college and subject references.",
                    ),
                    WorkflowStep(
                        AgentRoute.CONTENT_GENERATION,
                        "Generate the missing laboratory-record content.",
                    ),
                    WorkflowStep(
                        AgentRoute.VALIDATION,
                        "Validate completeness, grounding, duplication, and format.",
                    ),
                ]
            )
        elif experiment.status != "validated":
            steps.append(
                WorkflowStep(
                    AgentRoute.VALIDATION,
                    "Generated content exists but has not been validated.",
                )
            )
        elif not experiment.generated_pdf or not experiment.generated_docx:
            steps.append(
                WorkflowStep(
                    AgentRoute.DOCUMENT_GENERATION,
                    "Validated content needs downloadable DOCX and PDF files.",
                )
            )

        next_agent = steps[0].agent if steps else AgentRoute.COMPLETE
        return WorkflowPlan(
            experiment_id=experiment.pk,
            next_agent=next_agent,
            steps=tuple(steps),
            warnings=warnings,
            context={
                "subject": experiment.subject,
                "title": experiment.title,
                "status": experiment.status,
                "document_ids": [document.pk for document in documents],
                "observation_document_ids": [
                    document.pk for document in completed_observations
                ],
                "missing_generated_sections": list(
                    self._missing(experiment, self.GENERATED_FIELDS)
                ),
            },
        )

    @staticmethod
    def _missing(experiment: Experiment, fields: Iterable[str]) -> tuple[str, ...]:
        return tuple(
            field_name
            for field_name in fields
            if not str(getattr(experiment, field_name, "")).strip()
        )

    @staticmethod
    def _documents_with_status(
        documents: Iterable[ExperimentDocument], status: str
    ) -> tuple[ExperimentDocument, ...]:
        return tuple(
            document for document in documents if document.extraction_status == status
        )
