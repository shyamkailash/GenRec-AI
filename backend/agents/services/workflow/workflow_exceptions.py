"""Workflow-specific exceptions."""


class WorkflowError(Exception):
    """Base exception for workflow execution."""


class WorkflowStateError(WorkflowError):
    """Raised when workflow state is invalid."""


class ExtractionFailure(WorkflowError):
    """Observation extraction failed."""


class PlanningFailure(WorkflowError):
    """Experiment planning failed."""


class RetrievalFailure(WorkflowError):
    """Context retrieval failed."""


class GenerationFailure(WorkflowError):
    """Content generation failed."""


class ValidationFailure(WorkflowError):
    """Validation failed."""


class DocumentGenerationFailure(WorkflowError):
    """Document generation failed."""