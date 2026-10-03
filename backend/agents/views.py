"""REST endpoints for agent workflow orchestration."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from experiments.models import Experiment

from .serializers import (
    ContentGenerationRequestSerializer,
    DocumentGenerationRequestSerializer,
    ExperimentPlanningRequestSerializer,
    PlannerRequestSerializer,
    RetrievalRequestSerializer,
    ValidationRequestSerializer,
)
from .services import PlannerAgent, PlannerError
from .services.content_generator import (
    ContentGenerationAgent,
    ContentGenerationError,
)
from .services.document_generation import (
    DocumentGenerationAgent,
    DocumentGenerationError,
)
from .services.experiment_planner import (
    ExperimentPlanningAgent,
    ExperimentPlanningError,
)
from .services.retrieval_agent import (
    RetrievalAgent,
    RetrievalAgentError,
)
from .services.validation_agent import (
    ValidationAgent,
    ValidationError,
)

class PlannerAPIView(APIView):
    """Return the ordered agent workflow for an existing experiment."""

    planner_class = PlannerAgent

    def post(self, request):
        serializer = PlannerRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        experiment = get_object_or_404(
            Experiment.objects.prefetch_related("documents"),
            pk=serializer.validated_data["experiment_id"],
        )

        try:
            plan = self.planner_class().plan(experiment)
        except PlannerError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(
            plan.to_dict(),
            status=status.HTTP_200_OK,
        )

class RetrievalAPIView(APIView):
    """Retrieve grounded RAG context for an experiment."""

    retrieval_agent_class = RetrievalAgent

    def post(self, request):
        serializer = RetrievalRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        experiment = get_object_or_404(
            Experiment.objects.prefetch_related(
                "documents"
            ),
            pk=serializer.validated_data[
                "experiment_id"
            ],
        )

        try:
            result = self.retrieval_agent_class().retrieve(
                experiment=experiment,
                limit_per_query=(
                    serializer.validated_data.get(
                        "limit_per_query",
                        3,
                    )
                ),
            )

        except RetrievalAgentError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(
            result.to_dict(),
            status=status.HTTP_200_OK,
        )

class ExperimentPlanningAPIView(APIView):
    """Create a deterministic generation plan for an experiment."""

    planning_agent_class = ExperimentPlanningAgent

    def post(self, request):
        serializer = ExperimentPlanningRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        experiment = get_object_or_404(
            Experiment.objects.prefetch_related("documents"),
            pk=serializer.validated_data["experiment_id"],
        )

        try:
            plan = self.planning_agent_class().plan(experiment)
        except ExperimentPlanningError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(
            plan.to_dict(),
            status=status.HTTP_200_OK,
        )


class ContentGenerationAPIView(APIView):
    """Generate laboratory-record content for an experiment."""

    content_agent_class = ContentGenerationAgent
    retrieval_agent_class = RetrievalAgent

    def post(self, request):
        serializer = ContentGenerationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        experiment = get_object_or_404(
            Experiment.objects.prefetch_related("documents"),
            pk=serializer.validated_data["experiment_id"],
        )

        retrieved_context = serializer.validated_data.get("retrieved_context", "")
        citations = []
        if not retrieved_context:
            try:
                retrieval_result = self.retrieval_agent_class().retrieve(experiment)
            except RetrievalAgentError:
                pass
            else:
                retrieved_context = retrieval_result.context
                citations = retrieval_result.to_dict()["citations"]

        try:
            result = self.content_agent_class().generate(
                experiment=experiment,
                retrieved_context=retrieved_context,
            )
            experiment.theory = result.theory
            experiment.algorithm = result.algorithm
            experiment.procedure = result.procedure
            experiment.program = result.program
            experiment.output = result.output
            experiment.result = result.result
            experiment.status = "generated"
            experiment.save(update_fields=[
                "theory", "algorithm", "procedure", "program", "output", "result", "status"
            ])
        except ContentGenerationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(
            {
                "theory": result.theory,
                "algorithm": result.algorithm,
                "procedure": result.procedure,
                "program": result.program,
                "output": result.output,
                "result": result.result,
                "citations": citations,
            },
            status=status.HTTP_200_OK,
        )


class ValidationAPIView(APIView):
    """Validate generated content for an experiment."""

    validation_agent_class = ValidationAgent

    def post(self, request):
        serializer = ValidationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        experiment = get_object_or_404(
            Experiment,
            pk=serializer.validated_data["experiment_id"],
        )

        try:
            result = self.validation_agent_class().validate(experiment)
            if result.is_valid:
                experiment.status = "validated"
                experiment.save(update_fields=["status"])
        except ValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(
            result.to_dict(),
            status=status.HTTP_200_OK,
        )


class DocumentGenerationAPIView(APIView):
    """Generate DOCX and PDF documents for a validated experiment."""

    document_agent_class = DocumentGenerationAgent

    def post(self, request):
        serializer = DocumentGenerationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        experiment = get_object_or_404(
            Experiment,
            pk=serializer.validated_data["experiment_id"],
        )

        try:
            result = self.document_agent_class().generate(experiment)
        except DocumentGenerationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(
            result.to_dict(),
            status=status.HTTP_200_OK,
        )
