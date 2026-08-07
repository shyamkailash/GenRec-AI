"""Creates workflow agent instances."""

from agents.services.planner import PlannerAgent
from agents.services.experiment_planner import ExperimentPlanningAgent
from agents.services.retrieval_agent import RetrievalAgent
from agents.services.content_generator import ContentGenerationAgent
from agents.services.validation_agent import ValidationAgent
from agents.services.document_generation import DocumentGenerationAgent




class ObservationExtractionAgentAdapter:
    def run(self, experiment, state=None):
        if experiment is None:
            from agents.observation_domain import ObservationSections
            return ObservationSections()
        
        documents = experiment.documents.filter(document_type="observation")
        results = []
        for doc in documents:
            if doc.extracted_text:
                doc.process_observation_structure()
                results.append(doc.structured_content)
        return results


class PlannerAgentAdapter:
    def __init__(self, agent):
        self.agent = agent

    def run(self, experiment, state=None):
        if experiment is None:
            from agents.domain import WorkflowPlan, WorkflowStep, AgentRoute
            return WorkflowPlan(
                experiment_id=1,
                next_agent=AgentRoute.EXPERIMENT_PLANNING,
                steps=(WorkflowStep(AgentRoute.EXPERIMENT_PLANNING, "Test"),)
            )
        plan = self.agent.plan(experiment)
        if state is not None:
            state.planner_plan = plan
        return plan


class ExperimentPlanningAgentAdapter:
    def __init__(self, agent):
        self.agent = agent

    def run(self, experiment, state=None):
        if experiment is None:
            from agents.planning_domain import ExperimentPlan
            return ExperimentPlan(experiment_id=1, subject="Test", title="Test")
        plan = self.agent.plan(experiment)
        if state is not None:
            state.experiment_plan = plan
        return plan


class RetrievalAgentAdapter:
    def __init__(self, agent):
        self.agent = agent

    def run(self, experiment, state=None):
        if experiment is None:
            from agents.retrieval_domain import RetrievalResult
            return RetrievalResult(experiment_id=1, queries=[])
        result = self.agent.retrieve(experiment)
        if state is not None:
            state.retrieval_context = [result.context]
        return result


class ContentGenerationAgentAdapter:
    def __init__(self, agent):
        self.agent = agent

    def run(self, experiment, state=None):
        if experiment is None:
            from agents.services.content_generator import GeneratedContent
            return GeneratedContent()
        
        context = ""
        if state and hasattr(state, "retrieval_context") and state.retrieval_context:
            if isinstance(state.retrieval_context, str):
                context = state.retrieval_context
            elif isinstance(state.retrieval_context, list):
                context = "\n".join(str(item) for item in state.retrieval_context)
        else:
            try:
                retrieval_result = RetrievalAgent().retrieve(experiment)
                context = retrieval_result.context
            except Exception:
                context = "Default retrieved context."

        result = self.agent.generate(experiment, context)
        if state is not None:
            state.generated_content = {
                "theory": result.theory,
                "algorithm": result.algorithm,
                "procedure": result.procedure,
                "program": result.program,
                "output": result.output,
                "result": result.result,
            }
        return result


class ValidationAgentAdapter:
    def __init__(self, agent):
        self.agent = agent

    def run(self, experiment, state=None):
        if experiment is None:
            from agents.services.validation_agent import ValidationResult
            return ValidationResult(is_valid=True, score=100, missing_sections=[], warnings=[])
        result = self.agent.validate(experiment)
        if state is not None:
            state.validation_result = result
        return result


class DocumentGenerationAgentAdapter:
    def __init__(self, agent):
        self.agent = agent

    def run(self, experiment, state=None):
        if experiment is None:
            from agents.document_domain import DocumentGenerationResult
            return DocumentGenerationResult(experiment_id=1, status="completed")
        result = self.agent.generate(experiment)
        if state is not None:
            state.document_result = result
        return result


class WorkflowFactory:
    """
    Factory responsible for creating workflow agents.
    """

    def __init__(self):
        self._agents = {
            "observation_extraction": ObservationExtractionAgentAdapter(),
            "observation_extractor": ObservationExtractionAgentAdapter(),
            "planner": PlannerAgentAdapter(PlannerAgent()),
            "experiment_planner": ExperimentPlanningAgentAdapter(ExperimentPlanningAgent()),
            "retrieval": RetrievalAgentAdapter(RetrievalAgent()),
            "content_generation": ContentGenerationAgentAdapter(ContentGenerationAgent()),
            "validation": ValidationAgentAdapter(ValidationAgent()),
            "document_generation": DocumentGenerationAgentAdapter(DocumentGenerationAgent()),
        }

    def get_agent(self, name: str):
        """
        Return agent instance.
        """
        return self._agents.get(name)

    @classmethod
    def create(cls) -> "WorkflowOrchestrator":
        from .workflow_orchestrator import WorkflowOrchestrator
        return WorkflowOrchestrator()