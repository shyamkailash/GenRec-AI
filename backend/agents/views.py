"""REST endpoints for agent workflow orchestration."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from experiments.models import Experiment

from .serializers import (
    ExperimentPlanningRequestSerializer,
    PlannerRequestSerializer,
    RetrievalRequestSerializer,
)
from .services import PlannerAgent, PlannerError
from .services.experiment_planner import (
    ExperimentPlanningAgent,
    ExperimentPlanningError,
)
from .services.retrieval_agent import (
    RetrievalAgent,
    RetrievalAgentError,
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
